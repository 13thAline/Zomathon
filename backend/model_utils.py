import pandas as pd
import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity

CSV_PATH = 'items.csv' 
NPY_PATH = 'final_backend_embeddings.npy' 

print("1. Loading Neural Embeddings & Catalog...")
df = pd.read_csv(CSV_PATH)
embeddings = np.load(NPY_PATH)

print("2. Building the Knowledge Graph Bouncer...")
def build_restaurant_graph(restaurant_id):
    G = nx.Graph()
    res_df = df[df['restaurant_id'] == restaurant_id]

    for _, row in res_df.iterrows():
        item_id = int(row['item_id'])
        G.add_node(item_id, type='item', data=row.to_dict())
        G.add_node(f"CUISINE_{row['cuisine_type']}", type='cuisine')
        G.add_node(f"CAT_{row['category']}", type='category')
        
        G.add_edge(item_id, f"CUISINE_{row['cuisine_type']}", weight=1.0)
        G.add_edge(item_id, f"CAT_{row['category']}", weight=1.0)

    # The Immutable Laws of Food (Based on the new Master Taxonomy)
    synergies = [
        ("CAT_Wet Curry", "CAT_Bread", 8.0),
        ("CAT_Wet Curry", "CAT_Starter", 3.0),
        ("CAT_Dry Main", "CAT_Side", 6.0),
        ("CAT_Fast Food Main", "CAT_Side", 8.0),
        ("CAT_Starter", "CAT_Dry Main", 4.0),
        ("CAT_Starter", "CAT_Fast Food Main", 4.0),
        ("CAT_Drink", "CAT_Fast Food Main", 3.0),
        ("CAT_Drink", "CAT_Starter", 3.0),
        ("CAT_Dessert", "CAT_Drink", 2.0)
    ]
    for u, v, w in synergies:
        G.add_edge(u, v, weight=w)
        
    return G

# Cache graphs in memory
graphs = {res_id: build_restaurant_graph(res_id) for res_id in df['restaurant_id'].unique()}

def get_meal_completion_recs(item_id, top_n=6):
    try:
        idx = df[df['item_id'] == int(item_id)].index[0]
    except IndexError:
        return []

    target_vec = embeddings[idx].reshape(1, -1)
    target_row = df.iloc[idx]
    res_id = target_row['restaurant_id']
    target_cuisine = target_row['cuisine_type']
    target_cat = target_row['category']
    
    if res_id not in graphs:
        return []
    G = graphs[res_id]

    # === STAGE 1: NEURAL NETWORK RECALL ===
    sim_scores = cosine_similarity(target_vec, embeddings).flatten()
    
    # === STAGE 2: GRAPH THEORY RE-RANKING ===
    try:
        pagerank_scores = nx.pagerank(G, personalization={int(item_id): 1.0}, weight='weight', alpha=0.85)
    except Exception:
        pagerank_scores = {}

    hybrid_scores = []
    seen_names = {str(target_row['name']).split('(')[0].strip().lower()}

    for i, row in df.iterrows():
        current_id = int(row['item_id'])
        
        if row['restaurant_id'] != res_id or current_id == int(item_id):
            continue
            
        clean_name = str(row['name']).split('(')[0].strip().lower()
        if clean_name in seen_names:
            continue
            
        # Cuisine Shield
        if row['cuisine_type'] != target_cuisine and row['category'] not in ['Drink', 'Dessert']:
            continue

        nn_score = sim_scores[i] 
        graph_score = pagerank_scores.get(current_id, 0.0) * 100 
        
        # 60% Neural Net / 40% Graph
        final_score = (nn_score * 0.6) + (graph_score * 0.4)
        
        # Hot vs Cold Drink Override
        if row['category'] == 'Drink':
            is_hot = any(w in clean_name for w in ['tea', 'coffee', 'hot'])
            if target_cuisine in ['Fast Food', 'Chinese'] and is_hot:
                final_score *= 0.01 

        if target_cat in ['Wet Curry', 'Dry Main', 'Fast Food Main', 'Bread'] and row['category'] == 'Dessert':
            final_score *= 0.4

        hybrid_scores.append((final_score, row.to_dict(), clean_name))

    hybrid_scores.sort(key=lambda x: x[0], reverse=True)
    
    final_recs = []
    for score, data, clean_name in hybrid_scores:
        final_recs.append(data)
        seen_names.add(clean_name)
        if len(final_recs) == top_n:
            break
            
    return final_recs