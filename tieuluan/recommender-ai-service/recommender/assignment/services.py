from __future__ import annotations

import os
from typing import Tuple

from .graph_rag_chat import GraphRAGChatService
from .neo4j_kb_graph import Neo4jKBGraphService


def build_services() -> Tuple[Neo4jKBGraphService, GraphRAGChatService]:
    neo4j_service = Neo4jKBGraphService(
        uri=os.getenv("NEO4J_URI", ""),
        username=os.getenv("NEO4J_USER", ""),
        password=os.getenv("NEO4J_PASSWORD", ""),
    )
    graph_rag_service = GraphRAGChatService(neo4j_service)
    return neo4j_service, graph_rag_service
