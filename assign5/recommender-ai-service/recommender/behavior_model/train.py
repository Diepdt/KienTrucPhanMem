"""
Training Script: Huấn luyện Behavior Model sử dụng dữ liệu từ Data Pipeline
"""
import os
import pickle
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
import json
from pathlib import Path

from .model import BehaviorNCFModel
from .data_pipeline import get_data_for_training


# Thư mục lưu mô hình
MODEL_DIR = Path(__file__).parent / 'pretrained_models'
MODEL_DIR.mkdir(exist_ok=True)


class InteractionDataset(Dataset):
    """Dataset cho việc training behavior model từ user-item interactions"""
    
    def __init__(self, interactions):
        """
        interactions: numpy array shape (n, 3) với columns [user_id, item_id, rating]
        """
        self.user_ids = torch.LongTensor(interactions[:, 0])
        self.item_ids = torch.LongTensor(interactions[:, 1])
        self.ratings = torch.FloatTensor(interactions[:, 2])
    
    def __len__(self):
        return len(self.user_ids)
    
    def __getitem__(self, idx):
        return {
            'user_id': self.user_ids[idx],
            'item_id': self.item_ids[idx],
            'rating': self.ratings[idx]
        }


class BehaviorModelTrainer:
    """Trainer class cho Behavior Model"""
    
    def __init__(self, num_users, num_items, embedding_dim=32, hidden_layers=[64, 32, 16]):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")
        
        self.num_users = num_users
        self.num_items = num_items
        
        # Khởi tạo mô hình
        self.model = BehaviorNCFModel(
            num_users=num_users,
            num_items=num_items,
            embedding_dim=embedding_dim,
            hidden_layers=hidden_layers
        ).to(self.device)
        
        # Hàm mất mát (Loss function) - Binary Cross Entropy
        self.criterion = nn.BCELoss()
        
        # Optimizer - Adam
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
    
    def train_epoch(self, train_loader):
        """Huấn luyện một epoch"""
        self.model.train()
        total_loss = 0.0
        
        for batch in train_loader:
            user_ids = batch['user_id'].to(self.device)
            item_ids = batch['item_id'].to(self.device)
            ratings = batch['rating'].to(self.device)
            
            # Forward pass
            predictions = self.model(user_ids, item_ids)
            loss = self.criterion(predictions, ratings)
            
            # Backward pass
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader):
        """Đánh giá trên validation set"""
        self.model.eval()
        total_loss = 0.0
        
        with torch.no_grad():
            for batch in val_loader:
                user_ids = batch['user_id'].to(self.device)
                item_ids = batch['item_id'].to(self.device)
                ratings = batch['rating'].to(self.device)
                
                predictions = self.model(user_ids, item_ids)
                loss = self.criterion(predictions, ratings)
                total_loss += loss.item()
        
        return total_loss / len(val_loader)
    
    def train(self, interactions, epochs=20, batch_size=32, validation_split=0.2):
        """
        Huấn luyện mô hình trên toàn bộ dữ liệu
        
        Args:
            interactions: numpy array shape (n, 3)
            epochs: số epoch huấn luyện
            batch_size: kích thước batch
            validation_split: tỷ lệ validation set
        """
        if len(interactions) == 0:
            print("❌ ERROR: No interactions to train on!")
            return False
        
        # Split dữ liệu
        train_data, val_data = train_test_split(
            interactions,
            test_size=validation_split,
            random_state=42
        )
        
        print(f"\nTraining set size: {len(train_data)}")
        print(f"Validation set size: {len(val_data)}\n")
        
        # Tạo DataLoaders
        train_dataset = InteractionDataset(train_data)
        val_dataset = InteractionDataset(val_data)
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Huấn luyện
        print("Starting training...\n")
        best_val_loss = float('inf')
        patience = 5
        patience_counter = 0
        
        for epoch in range(1, epochs + 1):
            train_loss = self.train_epoch(train_loader)
            val_loss = self.validate(val_loader)
            
            print(f"Epoch {epoch:2d}/{epochs} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_model('best_model')
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"\n⚠ Early stopping at epoch {epoch}")
                    break
        
        print("\n✓ Training completed!")
        return True
    
    def save_model(self, filename='behavior_model'):
        """Lưu mô hình"""
        output_path = MODEL_DIR / f'{filename}.pt'
        torch.save({
            'model_state': self.model.state_dict(),
            'num_users': self.num_users,
            'num_items': self.num_items,
            'model_config': {
                'num_users': self.num_users,
                'num_items': self.num_items,
                'embedding_dim': 32,
                'hidden_layers': [64, 32, 16]
            }
        }, output_path)
        print(f"✓ Model saved to {output_path}")
    
    def load_model(self, filename='best_model'):
        """Tải mô hình"""
        input_path = MODEL_DIR / f'{filename}.pt'
        if not input_path.exists():
            print(f"❌ Model file not found: {input_path}")
            return False
        
        checkpoint = torch.load(input_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state'])
        print(f"✓ Model loaded from {input_path}")
        return True


def train_behavior_model():
    """
    Main function: Lấy dữ liệu từ services, huấn luyện mô hình và lưu
    """
    print("\n" + "="*60)
    print("BEHAVIOR MODEL TRAINING PIPELINE")
    print("="*60 + "\n")
    
    # Bước 1: Lấy dữ liệu
    print("STEP 1: Fetching data from microservices")
    print("-" * 60)
    interactions, num_users, num_items, pipeline = get_data_for_training()
    
    if num_users == 0 or num_items == 0:
        print("❌ ERROR: Not enough data for training!")
        return False
    
    # Bước 2: Khởi tạo trainer
    print("\nSTEP 2: Initializing trainer")
    print("-" * 60)
    trainer = BehaviorModelTrainer(
        num_users=num_users,
        num_items=num_items,
        embedding_dim=32,
        hidden_layers=[64, 32, 16]
    )
    
    # Bước 3: Huấn luyện mô hình
    print("\nSTEP 3: Training model")
    print("-" * 60)
    success = trainer.train(
        interactions=interactions,
        epochs=30,
        batch_size=32,
        validation_split=0.2
    )
    
    if not success:
        return False
    
    # Bước 4: Lưu metadata và mappings
    print("\nSTEP 4: Saving metadata and mappings")
    print("-" * 60)
    
    # Lưu customer ID mapping
    with open(MODEL_DIR / 'customer_id_map.json', 'w') as f:
        json.dump(pipeline.customer_id_map, f)
    print("✓ Saved customer ID mapping")
    
    # Lưu item ID mapping
    with open(MODEL_DIR / 'item_id_map.json', 'w') as f:
        json.dump(pipeline.item_id_map, f)
    print("✓ Saved item ID mapping")
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETED SUCCESSFULLY!")
    print("="*60 + "\n")
    return True


if __name__ == '__main__':
    train_behavior_model()
