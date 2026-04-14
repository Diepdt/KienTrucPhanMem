import os
import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
from torch_geometric.data import Data

from .gnn_model import RecommenderGNN
from .data_pipeline import DataPipeline

MODEL_DIR = Path(__file__).parent / 'pretrained_models'
MODEL_DIR.mkdir(exist_ok=True)

class GNNTrainer:
    """
    Huấn luyện RecommenderGNN với toàn bộ đồ thị Users và Products
    """
    def __init__(self, num_users, num_items, embedding_dim=32):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_users = num_users
        self.num_items = num_items
        
        self.model = RecommenderGNN(num_users, num_items, embedding_dim).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.01)
        self.criterion = nn.BCELoss()
        
    def build_graph_data(self, interactions):
        """Tạo đối tượng Dữ liệu PyTorch Geometric từ ma trận tương tác"""
        user_nodes = []
        item_nodes = []
        ratings = []
        
        for interaction in interactions:
            u_id, i_id, r = interaction
            u_id = int(u_id)
            i_id = int(i_id)
            
            user_nodes.append(u_id)
            # Item id trong graph bị dịch đi một khoảng bằng số lượng Users
            item_nodes.append(i_id + self.num_users)
            ratings.append(float(r))
            
            # GNN Edge là vô hướng (Undirected)
            user_nodes.append(i_id + self.num_users)
            item_nodes.append(u_id)
            ratings.append(float(r))
            
        edge_index = torch.tensor([user_nodes, item_nodes], dtype=torch.long)
        edge_attr = torch.tensor(ratings, dtype=torch.float32)
        
        self.graph_data = Data(edge_index=edge_index, edge_attr=edge_attr).to(self.device)
        
    def train(self, epochs=50):
        self.model.train()
        print("Bắt đầu huấn luyện GNN...")
        
        for epoch in range(1, epochs + 1):
            self.optimizer.zero_grad()
            
            # 1. Lan truyền thông tin trên toàn bộ Đồ thị
            final_embeddings = self.model(self.graph_data.edge_index)
            
            # 2. Lấy ra các cạnh nối thực sự để tính Loss
            user_indices = self.graph_data.edge_index[0, :len(self.graph_data.edge_attr)//2]
            item_indices = self.graph_data.edge_index[1, :len(self.graph_data.edge_attr)//2] - self.num_users
            ratings = self.graph_data.edge_attr[:len(self.graph_data.edge_attr)//2]
            
            predictions = self.model.predict(final_embeddings, user_indices, item_indices)
            loss = self.criterion(predictions, ratings)
            
            loss.backward()
            self.optimizer.step()
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}/{epochs} | Loss: {loss.item():.4f}")
                
        self.save_model()
                
    def save_model(self):
        output_path = MODEL_DIR / 'gnn_best_model.pt'
        torch.save(self.model.state_dict(), output_path)
        print(f"✓ Đã lưu GNN Model tại {output_path}")