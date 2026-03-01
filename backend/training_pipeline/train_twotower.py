import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

print("Loading Data...")
items_df = pd.read_csv("master_items.csv")
interactions_df = pd.read_csv("interactions.csv")

# Create contiguous indices for PyTorch
user_mapping = {uid: i for i, uid in enumerate(interactions_df['user_id'].unique())}
item_mapping = {iid: i for i, iid in enumerate(items_df['item_id'].unique())}

num_users = len(user_mapping)
num_items = len(item_mapping)

# Map IDs in dataframes
interactions_df['user_idx'] = interactions_df['user_id'].map(user_mapping)
interactions_df['item_idx'] = interactions_df['item_id'].map(item_mapping)

print(f"Mapped {num_users} users and {num_items} items.")

# NLP TEXT EMBEDDINGS 
print("Extracting NLP Text Embeddings (SentenceTransformers)")
text_model = SentenceTransformer('all-MiniLM-L6-v2')

items_df['item_idx'] = items_df['item_id'].map(item_mapping)
items_df = items_df.sort_values('item_idx')

descriptions = items_df['description'].tolist()
text_embeddings = text_model.encode(descriptions, show_progress_bar=True)
text_embeddings_tensor = torch.tensor(text_embeddings, dtype=torch.float32)

print("Building Implicit Feedback Dataset...")
class BPRDataset(Dataset):
    def __init__(self, interactions, num_items):
        # Only use Add to Cart and Orders as strong positive signals
        positives = interactions[interactions['interaction_type'].isin(['add_to_cart', 'order'])]
        self.user_item_pairs = positives[['user_idx', 'item_idx']].drop_duplicates().values
        self.num_items = num_items

    def __len__(self):
        return len(self.user_item_pairs)

    def __getitem__(self, idx):
        user_idx, pos_item_idx = self.user_item_pairs[idx]
        # Negative Sampling: Grab a random item the user didn't interact with here
        neg_item_idx = np.random.randint(self.num_items)
        return torch.tensor(user_idx), torch.tensor(pos_item_idx), torch.tensor(neg_item_idx)

train_dataset = BPRDataset(interactions_df, num_items)
train_loader = DataLoader(train_dataset, batch_size=2048, shuffle=True)

print("Initializing Two-Tower Architecture...")
class TwoTowerModel(nn.Module):
    def __init__(self, num_users, num_items, text_embeddings):
        super().__init__()
        # User Tower
        self.user_embedding = nn.Embedding(num_users, 64)
        
        # Item Tower (Hybrid: 32D ID + 32D Text)
        self.item_id_embedding = nn.Embedding(num_items, 32)
        
        # Freeze text embeddings so they act as a stable anchor
        self.text_embedding = nn.Embedding.from_pretrained(text_embeddings, freeze=True)
        self.text_projection = nn.Sequential(
            nn.Linear(384, 128),
            nn.ReLU(),
            nn.Linear(128, 32)
        )

    def forward(self, user_idx, pos_item_idx, neg_item_idx):
        # Get User Vector
        user_vec = self.user_embedding(user_idx)
        
        # Get Positive Item Vector (ID + Compressed Text)
        pos_id_vec = self.item_id_embedding(pos_item_idx)
        pos_text_vec = self.text_projection(self.text_embedding(pos_item_idx))
        pos_item_vec = torch.cat([pos_id_vec, pos_text_vec], dim=1) # 32 + 32 = 64D
        
        # Get Negative Item Vector
        neg_id_vec = self.item_id_embedding(neg_item_idx)
        neg_text_vec = self.text_projection(self.text_embedding(neg_item_idx))
        neg_item_vec = torch.cat([neg_id_vec, neg_text_vec], dim=1)
        
        return user_vec, pos_item_vec, neg_item_vec

    def get_all_item_embeddings(self):
        # Extract the final 64D vectors for the FastAPI backend
        all_indices = torch.arange(self.item_id_embedding.num_embeddings).to(self.item_id_embedding.weight.device)
        id_vecs = self.item_id_embedding(all_indices)
        text_vecs = self.text_projection(self.text_embedding(all_indices))
        return torch.cat([id_vecs, text_vecs], dim=1).detach().cpu().numpy()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = TwoTowerModel(num_users, num_items, text_embeddings_tensor).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.005)

# BPR Loss Function (Bayesian Personalized Ranking)
def bpr_loss(user_vec, pos_item_vec, neg_item_vec):
    pos_scores = (user_vec * pos_item_vec).sum(dim=1)
    neg_scores = (user_vec * neg_item_vec).sum(dim=1)
    # Maximize distance between positive and negative items
    loss = -torch.nn.functional.logsigmoid(pos_scores - neg_scores).mean()
    return loss

#The Training Loop
epochs = 10
print(f"Commencing Training on {device} for {epochs} Epochs...")

for epoch in range(epochs):
    model.train()
    total_loss = 0
    
    for users, pos_items, neg_items in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
        users, pos_items, neg_items = users.to(device), pos_items.to(device), neg_items.to(device)
        
        optimizer.zero_grad()
        user_vec, pos_vec, neg_vec = model(users, pos_items, neg_items)
        loss = bpr_loss(user_vec, pos_vec, neg_vec)
        
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        
    print(f"Epoch {epoch+1} Loss: {total_loss/len(train_loader):.4f}")

# EXTRACTION
print("Extracting Final Matrix for Production...")
final_embeddings = model.get_all_item_embeddings()

# Save the matrix
np.save("final_backend_embeddings.npy", final_embeddings)
print("SUCCESS. Matrix Shape:", final_embeddings.shape)
print("Move the'final_backend_embeddings.npy' and 'master_items.csv' to the root backend directory")
print("Rename the 'master_items.csv' to 'items.csv'")
