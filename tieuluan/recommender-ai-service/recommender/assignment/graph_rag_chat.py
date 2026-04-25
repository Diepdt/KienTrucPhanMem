from __future__ import annotations

from typing import Dict, Optional

from recommender.models import ChatMessage

from .neo4j_kb_graph import Neo4jKBGraphService


class GraphRAGChatService:
    def __init__(self, graph_service: Neo4jKBGraphService):
        self.graph_service = graph_service

    def _build_prompt(self, customer_id: int, message: str, conversation_id: str) -> str:
        graph_facts = self.graph_service.context_for_user(customer_id, limit=8)
        history = ChatMessage.objects.filter(
            customer_id=customer_id,
            conversation_id=conversation_id,
        ).order_by("-created_at")[:8]
        history = list(reversed(history))

        history_text = "\n".join([f"{m.role}: {m.content}" for m in history])
        graph_text = "\n".join(f"- {fact}" for fact in graph_facts) or "- (khong co du lieu graph)"

        return (
            "Ban la tro ly AI thuong mai dien tu. "
            "Tra loi bang tieng Viet, ngan gon, de hieu.\n\n"
            f"Customer ID: {customer_id}\n"
            f"Conversation history:\n{history_text or '(trong)'}\n\n"
            "Knowledge from KB_Graph (Neo4j):\n"
            f"{graph_text}\n\n"
            f"User question: {message}\n"
            "Assistant response:"
        )

    def _local_rag_answer(self, customer_id: int, message: str, conversation_id: str) -> str:
        graph_facts = self.graph_service.context_for_user(customer_id, limit=8)
        recs = self.graph_service.recommend_products(customer_id, top_k=5)

        if not graph_facts and not recs:
            return (
                "Minh chua co du lieu hanh vi cua ban trong KB_Graph. "
                "Ban hay tim kiem, xem san pham hoac them vao gio hang truoc, "
                "sau do minh se goi y chinh xac hon."
            )

        lower_msg = message.lower()
        asking_purchase = any(k in lower_msg for k in ["mua", "purchase", "dat hang"])
        asking_cart = any(k in lower_msg for k in ["gio", "cart", "them"])

        lines = ["Phan tich nhanh tu KB_Graph cua ban:"]
        if graph_facts:
            lines.append("- Hanh vi gan day:")
            for fact in graph_facts[:4]:
                lines.append(f"  + {fact}")

        if recs:
            lines.append("- San pham de xuat (uu tien theo muc do tuong tac):")
            for item in recs[:3]:
                lines.append(f"  + Product #{item['product_id']} (score={item['score']:.0f})")

        if asking_purchase:
            lines.append("Goi y: Ban nen uu tien san pham co score cao nhat va so sanh them theo ngan sach.")
        elif asking_cart:
            lines.append("Goi y: Ban co the bo sung vao gio 1-2 san pham top score de theo doi gia.")
        else:
            lines.append("Ban muon minh loc tiep theo tam gia, muc dich su dung hay danh muc khong?")

        return "\n".join(lines)

    def _fallback_answer(self, customer_id: int, message: str) -> str:
        recs = self.graph_service.recommend_products(customer_id, top_k=5)
        if not recs:
            return "Minh chua co du lieu do thi cho ban. Ban hay tim kiem hoac them san pham vao gio de minh goi y tot hon."
        lines = ["Muc goi y dua tren KB_Graph:"]
        for r in recs[:5]:
            lines.append(f"- Product #{r['product_id']} (score={r['score']:.0f})")
        lines.append("Ban can minh loc tiep theo gia hoac muc dich su dung khong?")
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
        _ = prompt
        answer = self._local_rag_answer(customer_id, message, conversation_id)

        ChatMessage.objects.create(
            conversation_id=conversation_id,
            customer_id=customer_id,
            role="assistant",
            content=answer,
        )

        recs = self.graph_service.recommend_products(customer_id, top_k=5)
        return {
            "success": True,
            "conversation_id": conversation_id,
            "response": answer,
            "recommended_products": recs,
        }
