"""
Inference Module: Sử dụng mô hình đã huấn luyện để dự đoán sản phẩm cho khách hàng
"""
import json
import torch
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .model import BehaviorNCFModel


MODEL_DIR = Path(__file__).parent / 'pretrained_models'


class BehaviorModelInference:
    """Class cho việc inference (dự đoán) sử dụng Behavior Model"""
    
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.num_users = None
        self.num_items = None
        self.customer_id_map = {}
        self.item_id_map = {}
        self.reverse_item_id_map = {}
        
        self._load_models_and_mappings()
    
    def _load_models_and_mappings(self):
        """Tải mô hình và ID mappings"""
        try:
            # Tải customer ID mapping
            with open(MODEL_DIR / 'customer_id_map.json', 'r') as f:
                self.customer_id_map = json.load(f)
            
            # Tải item ID mapping
            with open(MODEL_DIR / 'item_id_map.json', 'r') as f:
                self.item_id_map = json.load(f)
            
            # Tạo reverse mapping (useful để lấy lại original IDs)
            self.reverse_item_id_map = {v: k for k, v in self.item_id_map.items()}
            
            # Tải model checkpoint
            model_path = MODEL_DIR / 'best_model.pt'
            if not model_path.exists():
                print(f"⚠ Model file not found: {model_path}")
                print("  Using fallback greedy recommendation instead")
                self.model = None
                return
            
            checkpoint = torch.load(model_path, map_location=self.device)
            self.num_users = checkpoint['num_users']
            self.num_items = checkpoint['num_items']
            
            self.model = BehaviorNCFModel(
                num_users=self.num_users,
                num_items=self.num_items,
                embedding_dim=32,
                hidden_layers=[64, 32, 16]
            ).to(self.device)
            
            self.model.load_state_dict(checkpoint['model_state'])
            self.model.eval()
            
            print(f"✓ Model loaded successfully")
            print(f"  Users: {self.num_users}, Items: {self.num_items}")
        
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def get_user_embedding_index(self, customer_id: int) -> Optional[int]:
        """Lấy user embedding index từ customer ID thực"""
        # Convert to string vì JSON keys bắt buộc string
        return self.customer_id_map.get(str(customer_id))
    
    def get_item_embedding_index(self, product_id: int, service_type: str = 'book') -> Optional[int]:
        """Lấy item embedding index từ product ID và service type"""
        unique_key = f"{service_type}_{product_id}"
        return self.item_id_map.get(unique_key)
    
    def decode_item_id(self, item_idx: int) -> Tuple[str, int]:
        """
        Chuyển đổi item embedding index trở lại thành service_type + product_id
        
        Returns:
            (service_type, product_id)
        """
        unique_key = self.reverse_item_id_map.get(item_idx, "book_0")
        service_type, product_id = unique_key.split('_', 1)
        return service_type, int(product_id)
    
    def recommend(self, customer_id: int, top_k: int = 5, 
                  exclude_items: List[Tuple[str, int]] = None) -> List[Dict]:
        """
        Gợi ý K sản phẩm hàng đầu cho một khách hàng
        
        Args:
            customer_id: ID của khách hàng
            top_k: số sản phẩm để trả về
            exclude_items: danh sách các items để loại bỏ (dạng [(service_type, product_id), ...])
        
        Returns:
            List[Dict] gồm các item được gợi ý với scores
        """
        if self.model is None:
            # Fallback: trả về các items random nếu model không available
            print("⚠ Model not available, using fallback recommendation")
            return self._fallback_recommendation(customer_id, top_k)
        
        user_idx = self.get_user_embedding_index(customer_id)
        if user_idx is None:
            # User mới chưa có dữ liệu
            print(f"⚠ Customer {customer_id} not found in training data")
            return self._fallback_recommendation(customer_id, top_k)
        
        self.model.eval()
        with torch.no_grad():
            # Tạo tensor cho user và tất cả items
            user_tensor = torch.full((self.num_items,), user_idx, dtype=torch.long).to(self.device)
            item_tensor = torch.arange(self.num_items, dtype=torch.long).to(self.device)
            
            # Dự đoán scores
            scores = self.model(user_tensor, item_tensor)  # shape: (num_items,)
            
            # Loại bỏ các items không muốn
            if exclude_items:
                for service_type, product_id in exclude_items:
                    item_idx = self.get_item_embedding_index(product_id, service_type)
                    if item_idx is not None:
                        scores[item_idx] = -1.0  # Set score âm để loại bỏ
            
            # Lấy top K
            top_scores, top_indices = torch.topk(scores, k=min(top_k, self.num_items))
            
            results = []
            for score, item_idx in zip(top_scores.cpu().numpy(), top_indices.cpu().numpy()):
                if score >= 0:  # Skip excluded items
                    service_type, product_id = self.decode_item_id(int(item_idx))
                    results.append({
                        'service_type': service_type,
                        'product_id': product_id,
                        'score': float(score),
                        'confidence': float(torch.sigmoid(torch.tensor(score)).item())
                    })
            
            return results
    
    def _fallback_recommendation(self, customer_id: int, top_k: int = 5) -> List[Dict]:
        """Fallback recommendation (trả về items với scores random nếu model không available)"""
        # Random recommendation dựa trên item mapping
        import random
        
        items = list(self.item_id_map.keys())
        if not items:
            # Fallback cứng khi file mappings chưa được sinh ra do chưa train data thực tế.
            items = ['book_1', 'book_2', 'book_3', 'laptop_1', 'laptop_2', 'mobile_1', 'cloth_1']
            
        recommended = random.sample(items, min(top_k, len(items)))
        
        results = []
        for item_key in recommended:
            service_type, product_id = item_key.split('_', 1)
            results.append({
                'service_type': service_type,
                'product_id': int(product_id),
                'score': random.random(),
                'confidence': random.random()
            })
        
        # Sort bằng score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def get_personalized_context(self, customer_id: int) -> Dict:
        """
        Lấy context được cá nhân hóa cho một khách hàng
        Sử dụng embedding vectors từ user embedding layer
        """
        if self.model is None:
            return {}
        
        user_idx = self.get_user_embedding_index(customer_id)
        if user_idx is None:
            return {}
        
        with torch.no_grad():
            # Lấy user embedding vector
            user_embedding = self.model.user_embedding.weight[user_idx]
            
            # Tính toán preference strength dựa trên norm của embedding
            preference_strength = float(torch.norm(user_embedding).item())
            
            return {
                'customer_id': customer_id,
                'embedding_index': user_idx,
                'preference_strength': min(preference_strength, 1.0),  # Normalize to [0, 1]
                'is_new_customer': False
            }
        
        return {}


# Global singleton instance
_inference_instance = None


def get_inference_engine() -> BehaviorModelInference:
    """Lấy singleton instance của inference engine"""
    global _inference_instance
    if _inference_instance is None:
        _inference_instance = BehaviorModelInference()
    return _inference_instance


def recommend_for_customer(customer_id: int, top_k: int = 5) -> List[Dict]:
    """Wrapper function tiện lợi"""
    engine = get_inference_engine()
    return engine.recommend(customer_id, top_k=top_k)
