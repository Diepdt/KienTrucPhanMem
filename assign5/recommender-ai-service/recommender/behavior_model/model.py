import torch
import torch.nn as nn

class BehaviorNCFModel(nn.Module):
    """
    Neural Collaborative Filtering model cho việc dự đoán sở thích khách hàng.
    Mô hình học các Embedding của User và Item (Sản phẩm) qua các lớp Dense (Tầng ẩn).
    """
    def __init__(self, num_users, num_items, embedding_dim=32, hidden_layers=[64, 32, 16]):
        super(BehaviorNCFModel, self).__init__()
        
        # User & Item Embeddings
        self.user_embedding = nn.Embedding(num_embeddings=num_users, embedding_dim=embedding_dim)
        self.item_embedding = nn.Embedding(num_embeddings=num_items, embedding_dim=embedding_dim)
        
        # Các lớp ẩn (Hidden layers) của Multi-Layer Perceptron (MLP)
        mlp_modules = []
        input_size = embedding_dim * 2 # Nối User embedding và Item embedding
        
        for layer_size in hidden_layers:
            mlp_modules.append(nn.Linear(input_size, layer_size))
            mlp_modules.append(nn.ReLU())
            mlp_modules.append(nn.Dropout(p=0.2))
            input_size = layer_size
            
        self.mlp_layers = nn.Sequential(*mlp_modules)
        
        # Output layer (Dự đoán xác suất mua/tương tác - score từ 0 tới 1)
        self.output_layer = nn.Sequential(
            nn.Linear(input_size, 1),
            nn.Sigmoid()
        )

    def forward(self, user_indices, item_indices):
        user_emb = self.user_embedding(user_indices)
        item_emb = self.item_embedding(item_indices)
        
        # Nối vector của user và item lại với nhau
        vector_concat = torch.cat([user_emb, item_emb], dim=-1)
        
        # Đưa qua các lớp MLP
        x = self.mlp_layers(vector_concat)
        
        # Dự đoán đầu ra
        prediction = self.output_layer(x)
        return prediction.squeeze()

# Hàm inference mẫu để sử dụng trong Django View
def recommend_products(model, user_id, all_item_ids, top_k=5):
    model.eval()
    with torch.no_grad():
        user_tensor = torch.tensor([user_id] * len(all_item_ids))
        item_tensor = torch.tensor(all_item_ids)
        
        scores = model(user_tensor, item_tensor)
        
        # Lấy top k sản phẩm có điểm dự đoán cao nhất
        top_scores, top_indices = torch.topk(scores, top_k)
        
        recommended_items = [all_item_ids[i] for i in top_indices.tolist()]
        return recommended_items
