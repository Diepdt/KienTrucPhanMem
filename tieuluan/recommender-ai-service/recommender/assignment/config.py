from __future__ import annotations

from pathlib import Path

# 8 behavior classes used for sequence classification (task a)
MODEL_ACTIONS = [
    "view",
    "click",
    "search",
    "add_to_cart",
    "update_quantity",
    "remove_cart",
    "purchase",
    "rate",
]

# Event types accepted by API ingestion (task d). Chat is kept for task c.
EVENT_TYPES = MODEL_ACTIONS + ["chat"]

EVENT_CHOICES = [(event, event.replace("_", " ").title()) for event in EVENT_TYPES]

NEO4J_RELATION_MAP = {
    "view": "VIEW",
    "click": "CLICK",
    "search": "SEARCH",
    "add_to_cart": "ADD_TO_CART",
    "update_quantity": "UPDATE_QUANTITY",
    "remove_cart": "REMOVE_CART",
    "purchase": "PURCHASE",
    "rate": "RATE",
    "chat": "CHAT",
}

DEFAULT_SEQ_LEN = 10
DEFAULT_BATCH_SIZE = 128
DEFAULT_EPOCHS = 12
DEFAULT_HIDDEN_DIM = 64
DEFAULT_LEARNING_RATE = 0.001
DEFAULT_SEED = 42


def default_artifact_dir(base_dir: Path) -> Path:
    return base_dir / "recommender" / "assignment" / "artifacts"
