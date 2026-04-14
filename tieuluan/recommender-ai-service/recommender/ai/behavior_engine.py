from collections import defaultdict
from math import exp
from typing import Dict, List, Tuple

from django.utils import timezone

from recommender.models import BehaviorEvent, Recommendation

from .constants import EVENT_WEIGHTS
from .product_catalog import fetch_all_products


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = exp(-x)
        return 1 / (1 + z)
    z = exp(x)
    return z / (1 + z)


class BehaviorRecommendationEngine:
    """
    Sequence-aware recommendation engine.

    The score follows weighted behavior aggregation:
      w(u,p) = alpha * clicks + beta * carts + gamma * purchases + rho * recent_bias
    """

    def _interaction_strength(self, event: BehaviorEvent) -> float:
        base = EVENT_WEIGHTS.get(event.event_type, 1.0)
        age_hours = max((timezone.now() - event.created_at).total_seconds() / 3600.0, 0.0)
        decay = 1.0 / (1.0 + age_hours / 72.0)
        return base * decay

    def _build_user_product_matrix(self, customer_id: int) -> Dict[Tuple[str, int], float]:
        scores: Dict[Tuple[str, int], float] = defaultdict(float)
        events = BehaviorEvent.objects.filter(customer_id=customer_id).order_by("created_at")
        for event in events:
            if not event.product_id:
                continue
            key = (event.service_type or "book", int(event.product_id))
            scores[key] += self._interaction_strength(event)
        return scores

    def _extract_query_preferences(self, customer_id: int) -> List[str]:
        queries = (
            BehaviorEvent.objects.filter(customer_id=customer_id, event_type="search")
            .exclude(query_text="")
            .order_by("-created_at")[:8]
        )
        tokens: List[str] = []
        for event in queries:
            tokens.extend([t.lower() for t in event.query_text.split() if len(t) > 2])
        return tokens

    def recommend(self, customer_id: int, top_k: int = 10) -> List[Dict]:
        product_scores = self._build_user_product_matrix(customer_id)
        query_tokens = self._extract_query_preferences(customer_id)
        products = fetch_all_products()

        if not products:
            return []

        recommendations: List[Dict] = []
        for product in products:
            key = (product["service_type"], int(product["product_id"]))
            behavior_score = product_scores.get(key, 0.0)

            text_blob = f"{product['name']} {product.get('description', '')}".lower()
            lexical_boost = sum(0.2 for token in query_tokens if token in text_blob)

            final_raw = behavior_score + lexical_boost
            confidence = _sigmoid(final_raw)
            if final_raw <= 0 and not query_tokens:
                continue

            recommendations.append(
                {
                    "service_type": product["service_type"],
                    "product_id": int(product["product_id"]),
                    "score": round(final_raw, 5),
                    "confidence": round(confidence, 5),
                    "reason": "behavior+query-model",
                    "product_name": product["name"],
                }
            )

        recommendations.sort(key=lambda x: x["score"], reverse=True)

        top = recommendations[:top_k]
        Recommendation.objects.filter(customer_id=customer_id).delete()
        Recommendation.objects.bulk_create(
            [
                Recommendation(
                    customer_id=customer_id,
                    service_type=item["service_type"],
                    product_id=item["product_id"],
                    score=item["score"],
                    reason=item["reason"],
                    metadata={"confidence": item["confidence"], "product_name": item["product_name"]},
                )
                for item in top
            ]
        )
        return top
