from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from torch.utils.data import DataLoader, Dataset

from recommender.assignment.config import MODEL_ACTIONS

ACTION_ORDER = MODEL_ACTIONS


@dataclass
class SplitData:
    x_action: np.ndarray
    x_product: np.ndarray
    y: np.ndarray


class _SequenceDataset(Dataset):
    def __init__(self, x_action: np.ndarray, x_product: np.ndarray, y: np.ndarray):
        self.x_action = torch.tensor(x_action, dtype=torch.long)
        self.x_product = torch.tensor(x_product, dtype=torch.long)
        self.y = torch.tensor(y, dtype=torch.long)

    def __len__(self) -> int:
        return len(self.y)

    def __getitem__(self, idx: int):
        return self.x_action[idx], self.x_product[idx], self.y[idx]


class _SequenceClassifier(nn.Module):
    def __init__(
        self,
        model_type: str,
        num_actions: int,
        num_products: int,
        action_emb_dim: int = 8,
        product_emb_dim: int = 16,
        hidden_dim: int = 64,
        num_layers: int = 1,
        dropout: float = 0.2,
    ):
        super().__init__()
        self.action_embedding = nn.Embedding(num_actions, action_emb_dim)
        self.product_embedding = nn.Embedding(num_products, product_emb_dim)
        input_dim = action_emb_dim + product_emb_dim

        if model_type == "rnn":
            self.encoder = nn.RNN(
                input_size=input_dim,
                hidden_size=hidden_dim,
                batch_first=True,
                num_layers=num_layers,
                nonlinearity="tanh",
                dropout=dropout if num_layers > 1 else 0.0,
            )
            out_dim = hidden_dim
        elif model_type == "lstm":
            self.encoder = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_dim,
                batch_first=True,
                num_layers=num_layers,
                dropout=dropout if num_layers > 1 else 0.0,
                bidirectional=False,
            )
            out_dim = hidden_dim
        elif model_type == "bilstm":
            self.encoder = nn.LSTM(
                input_size=input_dim,
                hidden_size=hidden_dim,
                batch_first=True,
                num_layers=num_layers,
                dropout=dropout if num_layers > 1 else 0.0,
                bidirectional=True,
            )
            out_dim = hidden_dim * 2
        else:
            raise ValueError("model_type must be rnn|lstm|bilstm")

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(out_dim, len(ACTION_ORDER)),
        )

    def forward(self, x_action: torch.Tensor, x_product: torch.Tensor) -> torch.Tensor:
        a_emb = self.action_embedding(x_action)
        p_emb = self.product_embedding(x_product)
        x = torch.cat([a_emb, p_emb], dim=-1)
        out, _ = self.encoder(x)
        return self.classifier(out[:, -1, :])


class SequenceTrainingService:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(__file__).resolve().parent / "artifacts"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @staticmethod
    def _set_seed(seed: int) -> None:
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    @staticmethod
    def _evaluate(y_true: Sequence[int], y_pred: Sequence[int]) -> Dict[str, float]:
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
            "f1_macro": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        }

    def _load_and_prepare(
        self,
        csv_path: Path,
        seq_len: int,
    ) -> Tuple[SplitData, SplitData, SplitData, Dict[str, int], Dict[str, int], Dict[str, int]]:
        df = pd.read_csv(csv_path)
        required = {"user_id", "product_id", "action", "timestamp"}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required}")

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", dayfirst=True)
        df = df.dropna(subset=["timestamp"])
        df["action"] = df["action"].astype(str).str.strip()
        df = df[df["action"].isin(ACTION_ORDER)]
        df["product_id"] = df["product_id"].astype(int)
        df = df.sort_values(["user_id", "timestamp"]).reset_index(drop=True)

        action_to_id = {a: i for i, a in enumerate(ACTION_ORDER)}
        products = sorted(df["product_id"].unique().tolist())
        product_to_id = {p: i for i, p in enumerate(products)}

        x_action: List[List[int]] = []
        x_product: List[List[int]] = []
        y: List[int] = []

        for _uid, group in df.groupby("user_id"):
            g = group.sort_values("timestamp")
            actions = [action_to_id[a] for a in g["action"].tolist()]
            prods = [product_to_id[p] for p in g["product_id"].tolist()]
            if len(actions) <= seq_len:
                continue
            for idx in range(seq_len, len(actions)):
                x_action.append(actions[idx - seq_len:idx])
                x_product.append(prods[idx - seq_len:idx])
                y.append(actions[idx])

        if not y:
            raise ValueError("No windows generated. Reduce seq_len or increase events.")

        x_action_arr = np.asarray(x_action, dtype=np.int64)
        x_product_arr = np.asarray(x_product, dtype=np.int64)
        y_arr = np.asarray(y, dtype=np.int64)

        total = len(y_arr)
        train_end = int(total * 0.70)
        val_end = int(total * 0.85)

        train = SplitData(x_action_arr[:train_end], x_product_arr[:train_end], y_arr[:train_end])
        val = SplitData(x_action_arr[train_end:val_end], x_product_arr[train_end:val_end], y_arr[train_end:val_end])
        test = SplitData(x_action_arr[val_end:], x_product_arr[val_end:], y_arr[val_end:])

        index_to_product = {idx: pid for pid, idx in product_to_id.items()}
        product_to_index = {str(pid): idx for pid, idx in product_to_id.items()}
        index_to_product_json = {str(idx): int(pid) for idx, pid in index_to_product.items()}

        vocab = {"num_actions": len(action_to_id), "num_products": len(product_to_id)}
        return train, val, test, vocab, product_to_index, index_to_product_json

    def _run_epoch(self, model: nn.Module, loader: DataLoader, criterion, optimizer=None):
        is_train = optimizer is not None
        model.train() if is_train else model.eval()

        total_loss = 0.0
        y_true: List[int] = []
        y_pred: List[int] = []

        with torch.set_grad_enabled(is_train):
            for a_seq, p_seq, labels in loader:
                a_seq = a_seq.to(self.device)
                p_seq = p_seq.to(self.device)
                labels = labels.to(self.device)

                logits = model(a_seq, p_seq)
                loss = criterion(logits, labels)

                if is_train:
                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()

                total_loss += loss.item() * labels.size(0)
                preds = torch.argmax(logits, dim=1)
                y_true.extend(labels.detach().cpu().tolist())
                y_pred.extend(preds.detach().cpu().tolist())

        avg_loss = total_loss / max(len(loader.dataset), 1)
        avg_acc = accuracy_score(y_true, y_pred)
        return avg_loss, avg_acc, y_true, y_pred

    def _plot_curves(self, history: Dict[str, List[float]], model_name: str) -> None:
        try:
            import matplotlib.pyplot as plt
        except Exception:
            return

        epochs = list(range(1, len(history["train_loss"]) + 1))

        plt.figure(figsize=(8, 5))
        plt.plot(epochs, history["train_loss"], label="Train Loss")
        plt.plot(epochs, history["val_loss"], label="Val Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title(f"Loss Curve - {model_name.upper()}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{model_name}_loss.png", dpi=140)
        plt.close()

        plt.figure(figsize=(8, 5))
        plt.plot(epochs, history["train_acc"], label="Train Accuracy")
        plt.plot(epochs, history["val_acc"], label="Val Accuracy")
        plt.xlabel("Epoch")
        plt.ylabel("Accuracy")
        plt.title(f"Accuracy Curve - {model_name.upper()}")
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{model_name}_accuracy.png", dpi=140)
        plt.close()

    def _plot_confusion(self, y_true: List[int], y_pred: List[int], model_name: str) -> None:
        try:
            import matplotlib.pyplot as plt
        except Exception:
            return

        cm = confusion_matrix(y_true, y_pred, labels=list(range(len(ACTION_ORDER))))
        plt.figure(figsize=(8, 6))
        plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
        plt.colorbar()
        ticks = np.arange(len(ACTION_ORDER))
        plt.xticks(ticks, ACTION_ORDER, rotation=45, ha="right")
        plt.yticks(ticks, ACTION_ORDER)
        plt.title(f"Confusion Matrix - {model_name.upper()}")
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{model_name}_confusion_matrix.png", dpi=140)
        plt.close()

    def _plot_comparison(self, results: List[Dict]) -> None:
        try:
            import matplotlib.pyplot as plt
        except Exception:
            return

        names = [r["model_name"].upper() for r in results]
        f1_vals = [r["metrics"]["f1_macro"] for r in results]
        acc_vals = [r["metrics"]["accuracy"] for r in results]

        x = np.arange(len(names))
        width = 0.35
        plt.figure(figsize=(8, 5))
        plt.bar(x - width / 2, acc_vals, width, label="Accuracy")
        plt.bar(x + width / 2, f1_vals, width, label="F1 Macro")
        plt.xticks(x, names)
        plt.ylim(0, 1)
        plt.title("Model Comparison")
        plt.ylabel("Score")
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.output_dir / "model_comparison.png", dpi=140)
        plt.close()

    def _train_model(
        self,
        model_name: str,
        train_loader: DataLoader,
        val_loader: DataLoader,
        test_loader: DataLoader,
        vocab: Dict[str, int],
        epochs: int,
        hidden_dim: int,
        lr: float,
    ) -> Dict:
        model = _SequenceClassifier(
            model_type=model_name,
            num_actions=vocab["num_actions"],
            num_products=vocab["num_products"],
            hidden_dim=hidden_dim,
        ).to(self.device)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
        best_val_f1 = -1.0
        best_state = None

        for _epoch in range(epochs):
            train_loss, train_acc, _, _ = self._run_epoch(model, train_loader, criterion, optimizer)
            val_loss, val_acc, val_true, val_pred = self._run_epoch(model, val_loader, criterion)
            val_scores = self._evaluate(val_true, val_pred)

            history["train_loss"].append(float(train_loss))
            history["val_loss"].append(float(val_loss))
            history["train_acc"].append(float(train_acc))
            history["val_acc"].append(float(val_acc))

            if val_scores["f1_macro"] > best_val_f1:
                best_val_f1 = val_scores["f1_macro"]
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

        if best_state is not None:
            model.load_state_dict(best_state)

        test_loss, test_acc, test_true, test_pred = self._run_epoch(model, test_loader, criterion)
        metrics = self._evaluate(test_true, test_pred)
        metrics["test_loss"] = float(test_loss)
        metrics["test_accuracy"] = float(test_acc)

        model_path = self.output_dir / f"{model_name}_best.pt"
        torch.save(model.state_dict(), model_path)

        self._plot_curves(history, model_name)
        self._plot_confusion(test_true, test_pred, model_name)

        return {
            "model_name": model_name,
            "model_path": str(model_path),
            "history": history,
            "metrics": metrics,
        }

    def train_from_csv(
        self,
        csv_path: Path,
        seq_len: int = 10,
        batch_size: int = 128,
        epochs: int = 12,
        hidden_dim: int = 64,
        lr: float = 0.001,
        seed: int = 42,
    ) -> Dict:
        self._set_seed(seed)
        train, val, test, vocab, product_to_index, index_to_product = self._load_and_prepare(csv_path, seq_len)

        train_loader = DataLoader(_SequenceDataset(train.x_action, train.x_product, train.y), batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(_SequenceDataset(val.x_action, val.x_product, val.y), batch_size=batch_size, shuffle=False)
        test_loader = DataLoader(_SequenceDataset(test.x_action, test.x_product, test.y), batch_size=batch_size, shuffle=False)

        results = []
        for name in ["rnn", "lstm", "bilstm"]:
            results.append(
                self._train_model(
                    model_name=name,
                    train_loader=train_loader,
                    val_loader=val_loader,
                    test_loader=test_loader,
                    vocab=vocab,
                    epochs=epochs,
                    hidden_dim=hidden_dim,
                    lr=lr,
                )
            )

        model_best = max(results, key=lambda r: r["metrics"]["f1_macro"])
        model_best_path = self.output_dir / "model_best.pt"
        model_best_path.write_bytes(Path(model_best["model_path"]).read_bytes())

        # Export runtime artifacts expected by recommender inference service.
        (self.output_dir / "product_to_index.json").write_text(
            json.dumps(product_to_index, indent=2),
            encoding="utf-8",
        )
        (self.output_dir / "index_to_product.json").write_text(
            json.dumps(index_to_product, indent=2),
            encoding="utf-8",
        )

        self._plot_comparison(results)

        payload = {
            "results": results,
            "model_best": {
                "name": model_best["model_name"],
                "path": str(model_best_path),
                "metrics": model_best["metrics"],
            },
            "dataset": {
                "csv_path": str(csv_path),
                "train_samples": int(len(train.y)),
                "val_samples": int(len(val.y)),
                "test_samples": int(len(test.y)),
                "seq_len": int(seq_len),
            },
            "artifacts": {
                "model_best": str(model_best_path),
                "product_to_index": str(self.output_dir / "product_to_index.json"),
                "index_to_product": str(self.output_dir / "index_to_product.json"),
            },
        }

        (self.output_dir / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

        summary = ["MODEL EVALUATION SUMMARY", "=" * 40, ""]
        for row in results:
            m = row["metrics"]
            summary.append(
                f"{row['model_name'].upper()}: "
                f"acc={m['accuracy']:.4f}, precision_macro={m['precision_macro']:.4f}, "
                f"recall_macro={m['recall_macro']:.4f}, f1_macro={m['f1_macro']:.4f}"
            )

        summary.extend([
            "",
            f"model_best = {model_best['model_name'].upper()}",
            "Reason: selected by highest F1 macro on test split.",
        ])
        (self.output_dir / "evaluation_summary.txt").write_text("\n".join(summary), encoding="utf-8")

        return payload
