from collections import defaultdict
from typing import Dict, List, Tuple

from django.db.models import F

from recommender.models import BehaviorEvent, GraphEdge, GraphNode


class GraphKnowledgeEngine:
    """Maintain and query semantic graph from behavior events."""

    REL_EVENT_TO_EDGE = {
        "view": "VIEWED",
        "click": "CLICKED",
        "add_to_cart": "ADDED_TO_CART",
        "purchase": "PURCHASED",
        "search": "SEARCHED",
        "chat": "CHATTED",
    }

    def _get_or_create_node(self, node_type: str, external_id: str, label: str, metadata=None) -> GraphNode:
        node, _ = GraphNode.objects.get_or_create(
            node_type=node_type,
            external_id=str(external_id),
            defaults={"label": label[:255], "metadata": metadata or {}},
        )
        return node

    def _upsert_weighted_edge(self, source: GraphNode, target: GraphNode, relation: str, delta_weight: float, metadata=None):
        edge, created = GraphEdge.objects.get_or_create(
            source=source,
            target=target,
            relation=relation,
            defaults={"weight": max(delta_weight, 0.0), "metadata": metadata or {}},
        )
        if not created:
            GraphEdge.objects.filter(pk=edge.pk).update(
                weight=F("weight") + float(max(delta_weight, 0.0)),
                metadata=metadata or edge.metadata,
            )

    def ingest_event(self, event: BehaviorEvent, event_weight: float):
        user_node = self._get_or_create_node("user", str(event.customer_id), f"User {event.customer_id}")

        if event.query_text:
            query_node = self._get_or_create_node("query", event.query_text.lower(), event.query_text)
            self._upsert_weighted_edge(user_node, query_node, "SEARCHED_QUERY", event_weight)

        if event.product_id:
            product_key = f"{event.service_type}:{event.product_id}"
            product_node = self._get_or_create_node(
                "product",
                product_key,
                f"{event.service_type}#{event.product_id}",
                metadata={"service_type": event.service_type, "product_id": event.product_id},
            )
            relation = self.REL_EVENT_TO_EDGE.get(event.event_type, "INTERACTED")
            self._upsert_weighted_edge(user_node, product_node, relation, event_weight)

            category = event.service_type or "unknown"
            category_node = self._get_or_create_node("category", category, category.title())
            self._upsert_weighted_edge(product_node, category_node, "BELONGS_TO", 1.0)

    def rebuild_from_events(self):
        GraphEdge.objects.all().delete()
        GraphNode.objects.all().delete()

        for event in BehaviorEvent.objects.order_by("created_at"):
            event_weight = float(event.payload.get("weight", 1.0))
            self.ingest_event(event=event, event_weight=event_weight)

    def get_user_graph_facts(self, customer_id: int, top_k: int = 8) -> List[str]:
        try:
            user = GraphNode.objects.get(node_type="user", external_id=str(customer_id))
        except GraphNode.DoesNotExist:
            return []

        edges = (
            GraphEdge.objects.filter(source=user)
            .select_related("target")
            .order_by("-weight")[:top_k]
        )

        facts = []
        for edge in edges:
            facts.append(f"User {customer_id} -[{edge.relation}:{edge.weight:.2f}]-> {edge.target.label}")
        return facts

    def get_neighbors_for_text(self, text: str, top_k: int = 5) -> List[str]:
        words = [w.strip().lower() for w in text.split() if len(w.strip()) > 2]
        if not words:
            return []

        candidates = GraphNode.objects.filter(label__iregex="|".join(words))[:20]
        score_map: Dict[str, float] = defaultdict(float)

        for node in candidates:
            for edge in GraphEdge.objects.filter(source=node).select_related("target")[:5]:
                key = f"{node.label} -[{edge.relation}]-> {edge.target.label}"
                score_map[key] += edge.weight

        ranked: List[Tuple[str, float]] = sorted(score_map.items(), key=lambda x: x[1], reverse=True)
        return [row[0] for row in ranked[:top_k]]
