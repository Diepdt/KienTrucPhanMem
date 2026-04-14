import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple

KB_DIR = Path(__file__).parent / 'knowledge_base'

class GraphStore:
    """Quản lý in-memory Property Graph cho Knowledge Base"""
    
    def __init__(self):
        # edges format: source_node -> list of (relation, target_node)
        self.edges: Dict[str, List[Tuple[str, str]]] = {}
        self.nodes: Set[str] = set()
        self.is_ready = False
        self._load_graph()

    def _load_graph(self):
        graph_path = KB_DIR / 'graph_db.json'
        if graph_path.exists():
            with open(graph_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.edges = data.get('edges', {})
                self.nodes = set(data.get('nodes', []))
            self.is_ready = True
            print(f"✓ GraphStore loaded - {len(self.nodes)} nodes, {sum(len(v) for v in self.edges.values())} edges")

    def add_triple(self, source: str, relation: str, target: str):
        """Thêm một mối quan hệ (triple) vào đồ thị"""
        source = str(source).strip()
        target = str(target).strip()
        
        self.nodes.add(source)
        self.nodes.add(target)
        
        if source not in self.edges:
            self.edges[source] = []
        
        triple = (relation, target)
        if triple not in self.edges[source]:
            self.edges[source].append(triple)
            
        # Thêm liên kết ngược để dễ traverse
        if target not in self.edges:
            self.edges[target] = []
        reverse_triple = (f"REVERSE_{relation}", source)
        if reverse_triple not in self.edges[target]:
            self.edges[target].append(reverse_triple)

    def save_graph(self):
        KB_DIR.mkdir(exist_ok=True)
        graph_path = KB_DIR / 'graph_db.json'
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump({
                'nodes': list(self.nodes),
                'edges': self.edges
            }, f, ensure_ascii=False, indent=2)
        self.is_ready = True

    def search_subgraph(self, query: str, depth: int = 1) -> List[str]:
        """Tìm các Node/Thực thể có trong query và rẽ nhánh lấy thông tin"""
        if not self.is_ready:
            return []

        query_lower = query.lower()
        matched_nodes = []
        facts = []
        
        # 1. Trích xuất Entity: Tìm các node xuất hiện trong câu hỏi
        for node in self.nodes:
            # Lọc bỏ các node quá ngắn hoặc quá chung chung
            if len(node) > 3 and node.lower() in query_lower:
                matched_nodes.append(node)
                
        # 2. Duyệt đồ thị (Traverse): Lấy các facts từ các node tìm được
        visited = set(matched_nodes)
        for start_node in matched_nodes:
            if start_node in self.edges:
                for relation, target in self.edges[start_node]:
                    if not relation.startswith("REVERSE_"):
                        facts.append(f"[{start_node}] -> {relation} -> [{target}]")
                    else:
                        facts.append(f"[{target}] -> {relation.replace('REVERSE_', '')} -> [{start_node}]")
                        
        return list(set(facts)) # Xóa Facts trùng lặp

def get_graph_store():
    # Singleton pattern tương tự vector store
    global _GRAPH_STORE_INSTANCE
    if '_GRAPH_STORE_INSTANCE' not in globals():
        _GRAPH_STORE_INSTANCE = GraphStore()
    return _GRAPH_STORE_INSTANCE
