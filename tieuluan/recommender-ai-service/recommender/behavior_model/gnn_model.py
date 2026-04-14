import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
import torch.nn as nn

class RecommenderGNN(nn.Module):
    """
    Graph Neural Network model thay thế cho NCF cũ.
    Học embedding của User và Product thông qua cấu trúc Đồ thị (GCN).
    """
    def __init__(self, num_users, num_items, embedding_dim=32):
        super(RecommenderGNN, self).__init__()
        self.num_users = num_users
        self.num_items = num_items
        self.total_nodes = num_users + num_items
        
        # Khởi tạo ma trận đặc trưng ban đầu (Node features) cho tất cả user và item
        self.node_embeddings = nn.Parameter(torch.rand((self.total_nodes, embedding_dim)))
        
        # Các lớp Convolution của Graph
        self.conv1 = GCNConv(embedding_dim, 64)
        self.conv2 = GCNConv(64, embedding_dim)

    def forward(self, edge_index):
        # Truyền node_features qua các mạng tích chập đồ thị
        x = self.node_embeddings
        
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.2, training=self.training)
        
        x = self.conv2(x, edge_index)
        
        # Output x là embedding đã được GNN "nhào nặn" từ thông tin hàng xóm
        return x

    def predict(self, final_embeddings, user_indices, item_indices):
        """Tính điểm phù hợp (score) bằng Dot Product giữa User và Item"""
        # Node id của Item bị dịch đi một khoảng bằng num_users
        real_item_indices = item_indices + self.num_users
        
        user_emb = final_embeddings[user_indices]
        item_emb = final_embeddings[real_item_indices]
        
        # Dot product
        scores = torch.sum(user_emb * item_emb, dim=-1)
        return torch.sigmoid(scores)
