from typing import List, Dict, Any, Optional

from recommender.assignment.neo4j_kb_graph import Neo4jKBGraphService


class KnowledgeGraphService:
    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.service = Neo4jKBGraphService(uri=uri, username=username, password=password)

    def recommend_products(self, user_id: int, top_k: int = 10) -> List[Dict[str, Any]]:
        try:
            return self.service.recommend_products(user_id, top_k=top_k)
        except Exception:
            return []

    def context_for_user(self, user_id: int, limit: int = 8) -> List[str]:
        try:
            return self.service.context_for_user(user_id, limit=limit)
        except Exception:
            return []

    def search_products_by_keyword(self, keyword: str, top_k: int = 10) -> List[int]:
        # naive implementation: try to match Product nodes with a 'name' property containing keyword
        try:
            q = """
            MATCH (p:Product)
            WHERE toLower(p.name) CONTAINS toLower($kw)
            RETURN p.id AS product_id LIMIT $top_k
            """
            with self.service._driver() as driver:
                with driver.session() as session:
                    rows = session.run(q, kw=keyword, top_k=top_k).data()
            return [int(r["product_id"]) for r in rows if r.get("product_id") is not None]
        except Exception:
            return []

    def similar_products(self, product_id: int, top_k: int = 10) -> List[int]:
        # delegate to neo4j relationships if available
        try:
            # simple pattern: products connected to same users
            q = """
            MATCH (u:User)-[]->(p:Product {id: $pid})<-[]-(u2:User)-[]->(other:Product)
            RETURN other.id AS pid, count(*) AS score
            ORDER BY score DESC LIMIT $top_k
            """
            with self.service._driver() as driver:
                with driver.session() as session:
                    rows = session.run(q, pid=int(product_id), top_k=top_k).data()
            return [int(r["pid"]) for r in rows if r.get("pid") is not None]
        except Exception:
            return []
