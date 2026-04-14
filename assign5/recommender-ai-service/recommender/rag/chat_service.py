"""
RAG Chat Service: Chat với khách hàng bằng retrieval-augmented generation
"""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime

from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from .vector_store import get_vector_store
from ..behavior_model import get_inference_engine


# Initialize embedding model and API client
EMBEDDING_MODEL = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


class RAGChatService:
    """Service xử lý chat sử dụng RAG"""
    
    def __init__(self):
        self.vector_store = get_vector_store()
        self.behavior_model = get_inference_engine()
        
        # Setup Gemini API (same as agent-service)
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY chưa được cấu hình. "
                "Lấy key miễn phí tại https://aistudio.google.com/app/apikey"
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Chat history per customer
        self.chat_histories = {}
    
    def _get_chat_history(self, customer_id: int) -> List[Dict]:
        """Lấy lịch sử chat của khách hàng"""
        if customer_id not in self.chat_histories:
            self.chat_histories[customer_id] = []
        return self.chat_histories[customer_id]
    
    def _add_to_history(self, customer_id: int, role: str, content: str):
        """Thêm message vào lịch sử chat"""
        history = self._get_chat_history(customer_id)
        history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        # Giữ lịch sử tối đa 20 messages
        if len(history) > 20:
            self.chat_histories[customer_id] = history[-20:]
    
    def _retrieve_context(self, query: str, customer_id: int = None, top_k: int = 5) -> str:
        """
        Lấy ngữ cảnh (documents) liên quan đến query từ KB
        """
        if not self.vector_store.is_ready:
            return ""
        
        # Embedding query
        query_embedding = EMBEDDING_MODEL.encode(query)
        
        # Tìm kiếm documents liên quan
        relevant_docs = self.vector_store.similarity_search(query_embedding, k=top_k)
        
        # Format context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(f"- {doc['text']}")
        
        context = "\n".join(context_parts)
        return context
    
    def _get_personalization_info(self, customer_id: int) -> str:
        """
        Lấy thông tin cá nhân hóa dựa trên behavior model
        """
        try:
            # Lấy gợi ý sản phẩm dựa trên hành vi
            recommendations = self.behavior_model.recommend(customer_id, top_k=3)
            
            # Lấy preference context
            pref_context = self.behavior_model.get_personalized_context(customer_id)
            
            if not recommendations:
                return ""
            
            # Format personalization info
            info_parts = ["Based on your shopping history and preferences:"]
            
            for rec in recommendations:
                service = rec['service_type'].capitalize()
                confidence = rec['confidence']
                info_parts.append(
                    f"- You might be interested in {service} products (confidence: {confidence:.0%})"
                )
            
            return "\n".join(info_parts)
        
        except Exception as e:
            print(f"Error getting personalization info: {e}")
            return ""
    
    def chat(self, customer_id: int, message: str, conversation_id: str = None) -> Dict:
        """
        Xử lý chat message từ khách hàng
        
        Args:
            customer_id: ID của khách hàng
            message: message từ user
            conversation_id: optional conversation ID để tracking
        
        Returns:
            Dict gồm:
            - response: câu trả lời từ AI
            - recommended_products: các sản phẩm được gợi ý (nếu có)
            - conversation_id: ID của conversation
        """
        
        # Thêm user message vào history
        self._add_to_history(customer_id, 'user', message)
        
        # Lấy context từ KB
        retrieved_context = self._retrieve_context(message, customer_id, top_k=5)
        
        # Lấy personalization info
        personalization = self._get_personalization_info(customer_id)
        
        # Xây dựng system prompt
        system_prompt = f"""Bạn là một trợ lý khách hàng e-commerce thân thiện và tư vấn sản phẩm.

Vai trò của bạn:
1. Trả lời câu hỏi về sản phẩm và dịch vụ của công ty
2. Giúp khách hàng tìm sản phẩm phù hợp với nhu cầu
3. Cung cấp thông tin về vận chuyển, thanh toán, chính sách
4. Gợi ý sản phẩm cá nhân hóa

Danh mục sản phẩm: Sách, Laptop, Điện thoại, Quần áo
Dịch vụ: Giao hàng nhanh, Thanh toán linh hoạt, Hoàn trả 30 ngày, Hỗ trợ 24/7

{personalization}

QUAN TRỌNG:
- Luôn thân thiện và helpful
- Sử dụng thông tin từ knowledge base khi khách hỏi chi tiết sản phẩm/giá
- Dùng lịch sử mua của khách để gợi ý cá nhân
- Trả lời bằng tiếng Việt
- Nếu không biết, hãy thành thật

Thông tin Knowledge Base:
{retrieved_context}
"""
        
        # Prepare prompt for Gemini
        history = self._get_chat_history(customer_id)
        
        # Build full prompt with history
        history_text = ""
        for hist_msg in history[-10:]:
            if hist_msg['role'] in ['user', 'assistant']:
                role = "Khách hàng" if hist_msg['role'] == 'user' else "Trợ lý AI"
                history_text += f"\n{role}: {hist_msg['content']}"
        
        full_prompt = f"{system_prompt}\n\n--- Lịch sử cuộc trò chuyện ---{history_text}\n\nKhách hàng: {message}\n\nTrợ lý AI:"
        
        # Call Gemini API (same as agent-service)
        try:
            response = self.model.generate_content(full_prompt)
            
            assistant_message = response.text
            
            # Thêm AI response vào history
            self._add_to_history(customer_id, 'assistant', assistant_message)
            
            # Lấy sản phẩm được gợi ý
            recommendations = self.behavior_model.recommend(customer_id, top_k=5)
            
            return {
                'response': assistant_message,
                'recommended_products': recommendations,
                'conversation_id': conversation_id or f"conv_{customer_id}_{datetime.now().timestamp()}",
                'success': True
            }
        
        except Exception as e:
            error_msg = f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn: {str(e)}"
            print(f"Error calling Gemini API: {e}")
            return {
                'response': error_msg,
                'recommended_products': [],
                'conversation_id': conversation_id,
                'success': False,
                'error': str(e)
            }
    
    def get_quick_answer(self, query: str) -> str:
        """
        Nhanh chóng trả lời câu hỏi mà không cần cá nhân hóa
        Sử dụng cho FAQ hoặc general inquiries
        """
        try:
            # Lấy context
            retrieved_context = self._retrieve_context(query, top_k=3)
            
            system_prompt = f"""Bạn là một trợ lý e-commerce tư vấn.
Trả lời câu hỏi dưới đây dựa trên thông tin được cung cấp:

{retrieved_context}

Hãy tóm gọn và helpful. Nếu không có thông tin, hãy nói rõ."""
            
            full_prompt = f"{system_prompt}\n\nCâu hỏi: {query}\n\nTrả lời:"
            
            response = self.model.generate_content(full_prompt)
            
            return response.text
        
        except Exception as e:
            return f"Xin lỗi, tôi không thể xử lý yêu cầu của bạn lúc này: {str(e)}"
    
    def clear_history(self, customer_id: int):
        """Xóa lịch sử chat của khách hàng"""
        if customer_id in self.chat_histories:
            self.chat_histories[customer_id] = []


# Global singleton
_rag_service_instance = None


def get_rag_service() -> RAGChatService:
    """Lấy singleton instance của RAG service"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGChatService()
    return _rag_service_instance


def chat_with_customer(customer_id: int, message: str) -> Dict:
    """Wrapper function"""
    service = get_rag_service()
    return service.chat(customer_id, message)
