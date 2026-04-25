from pathlib import Path
import os
from typing import List, Dict

from recommender.models import BehaviorEvent

from recommender.ml_models.lstm_recommender import LSTMRecommender


class RecommendationService:
    def __init__(self, model_path: str | None = None):
        model_path = model_path or os.environ.get("LSTM_MODEL_PATH", "/app/models/lstm/model.pt")
        model_dir = Path(model_path).parent
        self.recommender = LSTMRecommender(model_dir=model_dir)

    def get_recommendations_for_user(self, user_id: int, top_k: int = 10) -> List[Dict]:
        # fetch recent behavior events for user
        rows = BehaviorEvent.objects.filter(customer_id=user_id).order_by("-created_at").values_list("product_id", flat=True)
        seq = [int(p) for p in rows if p is not None]
        if not seq:
            return []

        preds = self.recommender.predict(seq, top_k=top_k)
        return preds

    def get_recommendations_for_user_with_meta(self, user_id: int, top_k: int = 10) -> Dict:
        rows = BehaviorEvent.objects.filter(customer_id=user_id).order_by("-created_at").values_list("product_id", flat=True)
        seq = [int(p) for p in rows if p is not None]
        if not seq:
            return {
                "recommendations": [],
                "source": "lstm_model",
                "fallback_reason": None,
            }

        return self.recommender.predict_with_meta(seq, top_k=top_k)
