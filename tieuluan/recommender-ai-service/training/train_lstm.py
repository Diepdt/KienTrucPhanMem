"""
Training script to run LSTM training outside the API service.
This script uses the training.sequence_training.SequenceTrainingService (moved into training/).

Usage:
    python training/train_lstm.py --csv /path/to/data_user500.csv --output ./models/lstm

It will save best model and mapping files under the output directory.
"""
import argparse
from pathlib import Path

from training.sequence_training import SequenceTrainingService


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    p.add_argument("--output", default="./models/lstm")
    p.add_argument("--seq-len", type=int, default=10)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--epochs", type=int, default=12)
    p.add_argument("--hidden-dim", type=int, default=64)
    p.add_argument("--lr", type=float, default=0.001)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    trainer = SequenceTrainingService(output_dir=out_dir)
    trainer.train_from_csv(
        csv_path=Path(args.csv),
        seq_len=args.seq_len,
        batch_size=args.batch_size,
        epochs=args.epochs,
        hidden_dim=args.hidden_dim,
        lr=args.lr,
        seed=args.seed,
    )

    # The SequenceTrainingService saves model files in its output_dir. Copy the best model to model.pt
    model_best = out_dir / "model_best.pt"
    if model_best.exists():
        (out_dir / "model.pt").write_bytes(model_best.read_bytes())

    # Save simple mapping files if available (this depends on how training created artifacts)
    # If the trainer wrote a vocab mapping, copy it; otherwise leave user to prepare mapping.
    print("Training finished. Results saved to:", out_dir)


if __name__ == "__main__":
    main()
