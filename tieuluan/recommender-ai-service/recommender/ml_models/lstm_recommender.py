import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

import torch
import torch.nn as nn
from recommender.assignment.config import MODEL_ACTIONS


logger = logging.getLogger(__name__)


class _LSTMModelWrapper(nn.Module):
    def __init__(self, num_actions: int, num_products: int, action_emb_dim: int = 8, product_emb_dim: int = 16, hidden_dim: int = 64, num_layers: int = 1, dropout: float = 0.2):
        super().__init__()
        self.action_embedding = nn.Embedding(num_actions, action_emb_dim)
        self.product_embedding = nn.Embedding(num_products, product_emb_dim)
        input_dim = action_emb_dim + product_emb_dim
        self.encoder = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            batch_first=True,
            num_layers=num_layers,
            bidirectional=False,
        )
        out_dim = hidden_dim
        # classifier optional — many training variants exist; here we keep a projection
        self.classifier = nn.Linear(out_dim, num_products)

    def forward(self, x_action: torch.Tensor, x_product: torch.Tensor) -> torch.Tensor:
        a_emb = self.action_embedding(x_action)
        p_emb = self.product_embedding(x_product)
        x = torch.cat([a_emb, p_emb], dim=-1)
        out, _ = self.encoder(x)
        # use last timestep
        logits = self.classifier(out[:, -1, :])
        return logits


class LSTMRecommender:
    """Lightweight inference wrapper for a trained LSTM recommender.

    Expects model artifacts under a directory (default /app/models/lstm/):
      - model.pt
      - product_to_index.json
      - index_to_product.json

    If the saved model implements a custom `predict_products` method it will be used.
    Otherwise the wrapper will try to load state_dict into a compatible model and
    produce product logits; fallback is to return recent products.
    """

    def __init__(self, model_dir: str | Path | None = None, device: str | None = None):
        self.model_dir = Path(model_dir or os.environ.get("LSTM_MODEL_DIR", "/app/models/lstm"))
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = None
        self.product_to_index: Dict[str, int] = {}
        self.index_to_product: Dict[str, int] = {}
        self._missing_artifacts_warned = False
        self._fallback_warned = False
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        if not self.model_dir.exists():
            # no model artifacts available
            logger.warning("LSTM model directory not found at %s. Falling back to rule-based recommendations.", self.model_dir)
            return
        model_path = self.model_dir / "model.pt"
        p2i = self.model_dir / "product_to_index.json"
        i2p = self.model_dir / "index_to_product.json"

        if p2i.exists():
            with open(p2i, "r", encoding="utf-8") as fh:
                self.product_to_index = json.load(fh)
        if i2p.exists():
            with open(i2p, "r", encoding="utf-8") as fh:
                self.index_to_product = json.load(fh)

        if not model_path.exists():
            logger.warning("LSTM model file is missing at %s. Falling back to rule-based recommendations.", model_path)
            return

        saved = torch.load(model_path, map_location=self.device)
        # If saved is a module with predict_products, keep as is
        if hasattr(saved, "predict_products"):
            self.model = saved
            return

        # If saved is a dict that contains a model or state_dict
        if isinstance(saved, dict) and ("state_dict" in saved or any(k.startswith("encoder") or k.startswith("classifier") for k in saved.keys())):
            state = saved.get("state_dict", saved)
        else:
            state = saved

        # build a compatible model using sizes inferred from mapping and config
        num_products = max(len(self.product_to_index), 1)
        num_actions = len(MODEL_ACTIONS)
        hidden_dim = saved.get("hidden_dim") if isinstance(saved, dict) and "hidden_dim" in saved else 64

        model = _LSTMModelWrapper(num_actions=num_actions, num_products=num_products, hidden_dim=hidden_dim)
        try:
            if isinstance(state, dict):
                model.load_state_dict(state, strict=False)
        except Exception:
            # ignore load errors and keep fresh model
            pass

        model.to(self.device)
        model.eval()
        self.model = model

    @staticmethod
    def _recent_unique_fallback(product_sequence: List[int], top_k: int) -> List[Dict[str, Any]]:
        unique = []
        for p in reversed(product_sequence):
            if p not in unique:
                unique.append(p)
            if len(unique) >= top_k:
                break
        return [{"product_id": int(pid), "score": 1.0 - i * 0.01} for i, pid in enumerate(unique)]

    def predict_with_meta(self, product_sequence: List[int], top_k: int = 10) -> Dict[str, Any]:
        """Return recommendation results with transparent inference metadata."""
        if not self.model or not self.product_to_index:
            if not self._missing_artifacts_warned:
                logger.warning(
                    "Model artifacts unavailable (model_loaded=%s, mapping_size=%s). Using rule-based fallback.",
                    bool(self.model),
                    len(self.product_to_index),
                )
                self._missing_artifacts_warned = True
            return {
                "recommendations": self._recent_unique_fallback(product_sequence, top_k),
                "source": "rule_based_fallback",
                "fallback_reason": "model_not_loaded",
            }

        idxs = [self.product_to_index.get(str(p)) for p in product_sequence if str(p) in self.product_to_index]
        if not idxs:
            return {
                "recommendations": [],
                "source": "lstm_model",
                "fallback_reason": None,
            }

        import torch as _torch

        seq_len = len(idxs)
        a_seq = _torch.zeros((1, seq_len), dtype=_torch.long, device=self.device)
        p_seq = _torch.tensor([idxs], dtype=_torch.long, device=self.device)

        try:
            with _torch.no_grad():
                out = self.model(a_seq, p_seq)

            scores = out.squeeze(0).cpu().numpy()
            import numpy as _np

            top_idx = _np.argsort(-scores)[:top_k]
            results = []
            for i in top_idx:
                prod_id = int(self.index_to_product.get(str(int(i)), -1))
                if prod_id == -1:
                    prod_id = int(self.index_to_product.get(str(i), -1))
                results.append({"product_id": prod_id, "score": float(scores[int(i)])})

            return {
                "recommendations": results,
                "source": "lstm_model",
                "fallback_reason": None,
            }
        except Exception:
            if not self._fallback_warned:
                logger.warning("LSTM inference failed. Using rule-based fallback recommendations.", exc_info=True)
                self._fallback_warned = True
            return {
                "recommendations": self._recent_unique_fallback(product_sequence, top_k),
                "source": "rule_based_fallback",
                "fallback_reason": "inference_error",
            }

    def predict(self, product_sequence: List[int], top_k: int = 10) -> List[Dict[str, Any]]:
        """Return list of {product_id, score} ordered by score descending.

        product_sequence: list of product IDs (actual IDs, not indices)
        """
        return self.predict_with_meta(product_sequence, top_k=top_k)["recommendations"]
