import re
from typing import List, Dict, Any

from recommender.services.knowledge_graph_service import KnowledgeGraphService


class ChatbotService:
    def __init__(self, kg_service: KnowledgeGraphService):
        self.kg = kg_service

    def _extract_keywords(self, message: str) -> List[str]:
        tokens = re.findall(r"\w+", message.lower())
        keywords = [t for t in tokens if len(t) > 2]
        return keywords[:5]

    def chat(self, user_id: int, message: str, top_k: int = 8) -> Dict[str, Any]:
        keywords = self._extract_keywords(message)
        candidates = []
        for kw in keywords:
            found = self.kg.search_products_by_keyword(kw, top_k=top_k)
            for p in found:
                if p not in candidates:
                    candidates.append(p)

        # fallback: use graph-based recommendations for user
        if not candidates:
            recs = self.kg.recommend_products(user_id, top_k=top_k)
            candidates = [r["product_id"] for r in recs]

        # simple template reply
        if keywords:
            reply = f"Mình tìm thấy {len(candidates)} sản phẩm liên quan đến '{' '.join(keywords)}'."
        else:
            reply = "Mình đã tìm một số sản phẩm có thể phù hợp với bạn."

        return {"reply": reply, "recommended_products": candidates[:top_k]}
