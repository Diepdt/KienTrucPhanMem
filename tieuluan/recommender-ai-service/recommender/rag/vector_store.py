"""
Vector Store: Quản lý FAISS vector database và similarity search
"""
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠ FAISS not available, will use fallback similarity search")


KB_DIR = Path(__file__).parent / 'knowledge_base'


class VectorStore:
    """Quản lý vector store và similarity search"""
    
    def __init__(self):
        self.documents = []
        self.embeddings = None
        self.index = None
        self.is_ready = False
        
        self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        """Tải knowledge base từ files"""
        try:
            # Tải documents
            docs_path = KB_DIR / 'documents.json'
            if docs_path.exists():
                with open(docs_path, 'r', encoding='utf-8') as f:
                    docs_data = json.load(f)
                    self.documents = docs_data
            
            # Tải embeddings
            emb_path = KB_DIR / 'embeddings.npy'
            if emb_path.exists():
                self.embeddings = np.load(emb_path)
                
                # Xây dựng FAISS index
                if FAISS_AVAILABLE and self.embeddings is not None:
                    self._build_faiss_index()
                
                self.is_ready = True
                print(f"✓ VectorStore loaded - {len(self.documents)} documents, embeddings shape: {self.embeddings.shape}")
            else:
                print("⚠ No embeddings found - Knowledge base needs to be built first")
        
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            self.is_ready = False
    
    def _build_faiss_index(self):
        """Xây dựng FAISS index cho vector search"""
        if not FAISS_AVAILABLE or self.embeddings is None:
            return
        
        try:
            # Tạo index - sử dụng flat L2 distance
            embedding_dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(embedding_dim)
            
            # Thêm vectors vào index
            vectors = self.embeddings.astype('float32')
            self.index.add(vectors)
            
            print(f"✓ FAISS index built with {self.index.ntotal} vectors")
        
        except Exception as e:
            print(f"❌ Error building FAISS index: {e}")
            self.index = None
    
    def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Tìm kiếm K documents tương tự nhất với query
        
        Args:
            query_embedding: embedding vector của query
            k: số documents trả về
        
        Returns:
            List of (document, similarity_score, metadata) tuples
        """
        if not self.is_ready or len(self.documents) == 0:
            return []
        
        k = min(k, len(self.documents))
        
        # Sử dụng FAISS nếu có, nếu không dùng fallback
        if self.index is not None and FAISS_AVAILABLE:
            return self._faiss_search(query_embedding, k)
        else:
            return self._fallback_search(query_embedding, k)
    
    def _faiss_search(self, query_embedding: np.ndarray, k: int) -> List[Dict]:
        """FAISS-based similarity search"""
        query_vector = query_embedding.astype('float32').reshape(1, -1)
        
        # Tìm kiếm
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if 0 <= idx < len(self.documents):
                doc_data = self.documents[idx]
                similarity = 1.0 / (1.0 + float(dist))  # Convert distance to similarity score
                
                results.append({
                    'text': doc_data['text'],
                    'metadata': doc_data['metadata'],
                    'similarity_score': similarity,
                    'index': int(idx)
                })
        
        return results
    
    def _fallback_search(self, query_embedding: np.ndarray, k: int) -> List[Dict]:
        """Fallback similarity search sử dụng cosine similarity"""
        if self.embeddings is None:
            return []
        
        # Compute cosine similarity
        query_norm = np.linalg.norm(query_embedding)
        doc_norms = np.linalg.norm(self.embeddings, axis=1)
        
        similarities = np.dot(self.embeddings, query_embedding) / (doc_norms * query_norm + 1e-8)
        
        # Get top k
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            doc_data = self.documents[idx]
            results.append({
                'text': doc_data['text'],
                'metadata': doc_data['metadata'],
                'similarity_score': float(similarities[idx]),
                'index': int(idx)
            })
        
        return results
    
    def get_document_by_index(self, idx: int) -> Dict:
        """Lấy document theo index"""
        if 0 <= idx < len(self.documents):
            return self.documents[idx]
        return None
    
    def get_all_documents(self) -> List[Dict]:
        """Lấy tất cả documents"""
        return self.documents
    
    def get_documents_by_type(self, doc_type: str) -> List[Dict]:
        """Lấy documents theo type (product, policy, general)"""
        results = []
        for doc in self.documents:
            if doc['metadata'].get('type') == doc_type:
                results.append(doc)
        return results
    
    def get_documents_by_service(self, service: str) -> List[Dict]:
        """Lấy products từ một service cụ thể"""
        results = []
        for doc in self.documents:
            if doc['metadata'].get('service') == service:
                results.append(doc)
        return results


# Global singleton instance
_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """Lấy singleton instance của vector store"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
