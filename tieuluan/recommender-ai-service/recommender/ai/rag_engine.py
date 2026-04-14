import os
from collections import Counter
from math import sqrt
from typing import Dict, List, Optional

import requests

from recommender.models import ChatMessage, KnowledgeDocument

from .behavior_engine import BehaviorRecommendationEngine
from .graph_engine import GraphKnowledgeEngine


class RAGChatEngine:
    """Hybrid RAG engine using lexical retrieval + graph facts + behavior personalization."""

    def __init__(self):
        self.behavior_engine = BehaviorRecommendationEngine()
        self.graph_engine = GraphKnowledgeEngine()

    def _tokenize(self, text: str) -> List[str]:
        return [t.lower().strip(".,!?;:\"'()[]{}") for t in text.split() if t.strip()]

    def _vectorize(self, text: str) -> Counter:
        return Counter(self._tokenize(text))

    def _cosine(self, a: Counter, b: Counter) -> float:
        if not a or not b:
            return 0.0
        keys = set(a.keys()) | set(b.keys())
        dot = sum(a.get(k, 0) * b.get(k, 0) for k in keys)
        norm_a = sqrt(sum(v * v for v in a.values()))
        norm_b = sqrt(sum(v * v for v in b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _retrieve_docs(self, query: str, top_k: int = 5) -> List[Dict]:
        q_vec = self._vectorize(query)
        rows = KnowledgeDocument.objects.all()[:500]
        scored = []
        for row in rows:
            text = f"{row.title} {row.content}"
            score = self._cosine(q_vec, self._vectorize(text))
            if score <= 0:
                continue
            scored.append(
                {
                    "id": row.id,
                    "source": row.source,
                    "title": row.title,
                    "content": row.content,
                    "score": score,
                }
            )
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def _build_prompt(self, customer_id: int, message: str, conversation_id: str) -> str:
        docs = self._retrieve_docs(message, top_k=5)
        graph_facts = self.graph_engine.get_user_graph_facts(customer_id, top_k=6)
        semantic_facts = self.graph_engine.get_neighbors_for_text(message, top_k=4)
        recs = self.behavior_engine.recommend(customer_id, top_k=3)

        history = ChatMessage.objects.filter(
            customer_id=customer_id,
            conversation_id=conversation_id,
        ).order_by("-created_at")[:8]
        history = list(reversed(history))

        context_blocks = []
        if docs:
            context_blocks.append("Tai lieu lien quan:")
            for d in docs:
                context_blocks.append(f"- [{d['source']}] {d['title']}: {d['content'][:220]}")

        if graph_facts or semantic_facts:
            context_blocks.append("Su kien do thi tri thuc:")
            for fact in graph_facts + semantic_facts:
                context_blocks.append(f"- {fact}")

        if recs:
            context_blocks.append("Goi y hanh vi hien tai:")
            for rec in recs:
                context_blocks.append(
                    f"- {rec['service_type']}#{rec['product_id']} score={rec['score']} confidence={rec['confidence']}"
                )

        history_text = "\n".join([f"{m.role}: {m.content}" for m in history])

        prompt = (
            "Ban la tro ly AI cho thuong mai dien tu. "
            "Tra loi bang tieng Viet, ro rang, huu ich, khong biet thi noi khong biet.\n\n"
            f"Khach hang ID: {customer_id}\n"
            f"Lich su hoi thoai gan day:\n{history_text or '(trong)'}\n\n"
            f"Ngu canh RAG:\n{chr(10).join(context_blocks) or '(khong co)'}\n\n"
            f"Cau hoi moi: {message}\n"
            "Tra loi:"
        )
        return prompt

    def _call_gemini(self, prompt: str) -> Optional[str]:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return None

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.0-flash:generateContent"
        )
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ]
        }
        params = {"key": api_key}
        try:
            response = requests.post(url, json=payload, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts", [])
            if not parts:
                return None
            return parts[0].get("text")
        except Exception:
            return None

    def _fallback_answer(self, customer_id: int, message: str) -> str:
        docs = self._retrieve_docs(message, top_k=3)
        recs = self.behavior_engine.recommend(customer_id, top_k=3)

        lines = ["Mình da phan tich du lieu hanh vi va tri thuc hien co cho ban:"]
        if docs:
            lines.append("Thong tin lien quan:")
            for doc in docs:
                lines.append(f"- {doc['title']}: {doc['content'][:140]}")
        else:
            lines.append("- Chua tim thay tai lieu trung khop manh trong KB.")

        if recs:
            lines.append("Goi y san pham ca nhan hoa:")
            for rec in recs:
                lines.append(
                    f"- {rec['service_type']} #{rec['product_id']} (diem {rec['score']}, tin cay {rec['confidence']})"
                )

        lines.append("Neu ban muon, minh co the loc theo gia, nhu cau hoc tap, hoac muc dich su dung.")
        return "\n".join(lines)

    def chat(self, customer_id: int, message: str, conversation_id: Optional[str] = None) -> Dict:
        conversation_id = conversation_id or f"conv-{customer_id}"

        ChatMessage.objects.create(
            conversation_id=conversation_id,
            customer_id=customer_id,
            role="user",
            content=message,
        )

        prompt = self._build_prompt(customer_id, message, conversation_id)
        answer = self._call_gemini(prompt)
        if not answer:
            answer = self._fallback_answer(customer_id, message)

        ChatMessage.objects.create(
            conversation_id=conversation_id,
            customer_id=customer_id,
            role="assistant",
            content=answer,
        )

        recs = self.behavior_engine.recommend(customer_id, top_k=5)
        return {
            "conversation_id": conversation_id,
            "response": answer,
            "recommended_products": recs,
            "success": True,
        }
