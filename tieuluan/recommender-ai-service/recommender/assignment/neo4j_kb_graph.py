from __future__ import annotations

import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from recommender.models import BehaviorEvent

from .config import NEO4J_RELATION_MAP


class Neo4jKBGraphService:
    RELATION_MAP = NEO4J_RELATION_MAP

    def __init__(self, uri: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        self.uri = uri
        self.username = username
        self.password = password

    def _driver(self):
        try:
            from neo4j import GraphDatabase
        except Exception as exc:
            raise RuntimeError("neo4j driver is not installed. Install package 'neo4j'.") from exc

        if not self.uri or not self.username or not self.password:
            raise RuntimeError("Neo4j credentials are missing. Set NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD.")
        return GraphDatabase.driver(self.uri, auth=(self.username, self.password))

    def wait_until_ready(self, retries: int = 20, delay_seconds: float = 1.5) -> None:
        last_error = None
        for _ in range(max(retries, 1)):
            try:
                with self._driver() as driver:
                    driver.verify_connectivity()
                return
            except Exception as exc:
                last_error = exc
                time.sleep(delay_seconds)
        raise RuntimeError(f"Neo4j is not ready after retries: {last_error}")

    def ensure_constraints(self) -> None:
        with self._driver() as driver:
            with driver.session() as session:
                session.run("CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
                session.run("CREATE CONSTRAINT product_id_unique IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE")

    def clear_graph(self) -> None:
        with self._driver() as driver:
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")

    def graph_overview(self) -> Dict[str, object]:
        node_count_query = "MATCH (n) RETURN count(n) AS c"
        rel_count_query = "MATCH ()-[r]->() RETURN count(r) AS c"
        top_users_query = """
        MATCH (u:User)-[r]->()
        RETURN u.id AS user_id, count(r) AS interactions
        ORDER BY interactions DESC
        LIMIT 5
        """
        top_products_query = """
        MATCH ()-[r]->(p:Product)
        RETURN p.id AS product_id, count(r) AS interactions
        ORDER BY interactions DESC
        LIMIT 5
        """

        with self._driver() as driver:
            with driver.session() as session:
                node_count = int(session.run(node_count_query).single()["c"])
                relationship_count = int(session.run(rel_count_query).single()["c"])
                top_users = session.run(top_users_query).data()
                top_products = session.run(top_products_query).data()

        return {
            "node_count": node_count,
            "relationship_count": relationship_count,
            "action_distribution": self.action_distribution(),
            "top_users": [
                {"user_id": int(row["user_id"]), "interactions": int(row["interactions"])}
                for row in top_users
            ],
            "top_products": [
                {"product_id": int(row["product_id"]), "interactions": int(row["interactions"])}
                for row in top_products
            ],
        }

    def _upsert_event(self, tx, user_id: int, product_id: int, action: str, timestamp: str):
        relation = self.RELATION_MAP.get(action, "INTERACT")
        query = f"""
        MERGE (u:User {{id: $user_id}})
        MERGE (p:Product {{id: $product_id}})
        CREATE (u)-[:{relation} {{timestamp: $timestamp}}]->(p)
        """
        tx.run(query, user_id=int(user_id), product_id=int(product_id), timestamp=timestamp)

    def _write_batch_for_action(self, session, action: str, rows: List[Dict]) -> None:
        relation = self.RELATION_MAP[action]
        query = f"""
        UNWIND $rows AS row
        MERGE (u:User {{id: row.user_id}})
        MERGE (p:Product {{id: row.product_id}})
        CREATE (u)-[:{relation} {{timestamp: row.timestamp}}]->(p)
        """
        session.run(query, rows=rows)

    def ingest_dataframe(self, df: pd.DataFrame, batch_size: int = 1000, retries: int = 3) -> Dict[str, int]:
        if df.empty:
            return {"events": 0, "users": 0, "products": 0}

        self.ensure_constraints()

        rows_by_action: Dict[str, List[Dict]] = {action: [] for action in self.RELATION_MAP}
        for row in df.itertuples(index=False):
            action = str(row.action).strip()
            if action not in self.RELATION_MAP:
                continue
            ts = pd.to_datetime(row.timestamp, errors="coerce", dayfirst=False)
            if pd.isna(ts):
                continue
            rows_by_action[action].append(
                {
                    "user_id": int(row.user_id),
                    "product_id": int(row.product_id),
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )

        events_count = sum(len(rows) for rows in rows_by_action.values())
        if events_count == 0:
            return {"events": 0, "users": 0, "products": 0}

        for attempt in range(1, max(retries, 1) + 1):
            try:
                with self._driver() as driver:
                    with driver.session() as session:
                        for action, rows in rows_by_action.items():
                            if not rows:
                                continue
                            for start in range(0, len(rows), max(batch_size, 1)):
                                chunk = rows[start:start + max(batch_size, 1)]
                                self._write_batch_for_action(session, action, chunk)
                break
            except Exception:
                if attempt >= max(retries, 1):
                    raise
                time.sleep(1.5 * attempt)

        return {
            "events": events_count,
            "users": int(df["user_id"].nunique()),
            "products": int(df["product_id"].nunique()),
        }

    def ingest_csv(self, csv_path: Path, batch_size: int = 1000, retries: int = 3) -> Dict[str, int]:
        df = pd.read_csv(csv_path)
        required = {"user_id", "product_id", "action", "timestamp"}
        if not required.issubset(df.columns):
            raise ValueError(f"CSV must contain columns: {required}")
        return self.ingest_dataframe(df, batch_size=batch_size, retries=retries)

    def ingest_behavior_events(self, batch_size: int = 1000, retries: int = 3) -> Dict[str, int]:
        rows = BehaviorEvent.objects.values("customer_id", "product_id", "event_type", "created_at")
        payload = [
            {
                "user_id": int(r["customer_id"]),
                "product_id": int(r["product_id"]) if r["product_id"] is not None else None,
                "action": r["event_type"],
                "timestamp": r["created_at"],
            }
            for r in rows
            if r["product_id"] is not None
        ]
        if not payload:
            return {"events": 0, "users": 0, "products": 0}
        return self.ingest_dataframe(pd.DataFrame(payload), batch_size=batch_size, retries=retries)

    def ingest_event(self, customer_id: int, product_id: Optional[int], action: str, timestamp) -> Dict[str, int]:
        if product_id is None:
            return {"events": 0, "users": 0, "products": 0}
        if action not in self.RELATION_MAP:
            return {"events": 0, "users": 0, "products": 0}

        ts = pd.to_datetime(timestamp, errors="coerce", dayfirst=False)
        if pd.isna(ts):
            return {"events": 0, "users": 0, "products": 0}

        self.ensure_constraints()
        with self._driver() as driver:
            with driver.session() as session:
                session.execute_write(
                    self._upsert_event,
                    int(customer_id),
                    int(product_id),
                    action,
                    ts.strftime("%Y-%m-%dT%H:%M:%S"),
                )

        return {"events": 1, "users": 1, "products": 1}

    def recommend_products(self, user_id: int, top_k: int = 10) -> List[Dict]:
        query = """
        MATCH (u:User {id: $user_id})-[r]->(p:Product)
        WITH p, count(r) AS interaction_count
        RETURN p.id AS product_id, interaction_count
        ORDER BY interaction_count DESC
        LIMIT $top_k
        """
        with self._driver() as driver:
            with driver.session() as session:
                rows = session.run(query, user_id=int(user_id), top_k=int(top_k)).data()
        return [
            {
                "product_id": int(row["product_id"]),
                "score": float(row["interaction_count"]),
                "reason": "neo4j-graph-frequency",
            }
            for row in rows
        ]

    def context_for_user(self, user_id: int, limit: int = 8) -> List[str]:
        query = """
        MATCH (u:User {id: $user_id})-[r]->(p:Product)
        RETURN type(r) AS rel, p.id AS product_id, r.timestamp AS ts
        ORDER BY ts DESC
        LIMIT $limit
        """
        with self._driver() as driver:
            with driver.session() as session:
                rows = session.run(query, user_id=int(user_id), limit=int(limit)).data()
        return [f"User {user_id} {row['rel']} Product#{row['product_id']} at {row['ts']}" for row in rows]

    def action_distribution(self) -> Dict[str, int]:
        query = """
        MATCH ()-[r]->()
        RETURN type(r) AS rel, count(*) AS cnt
        ORDER BY cnt DESC
        """
        with self._driver() as driver:
            with driver.session() as session:
                rows = session.run(query).data()
        return {str(row["rel"]): int(row["cnt"]) for row in rows}
