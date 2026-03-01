import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

CSV_PATH = 'items.csv' 
NPY_PATH = 'final_backend_embeddings.npy' # Ensure this matches your actual .npy filename

print("Loading ML Matrix and Strict Taxonomy...")
df = pd.read_csv(CSV_PATH)
embeddings = np.load(NPY_PATH)

def get_meal_completion_recs(item_id, top_n=5):
    try:
        idx = df[df['item_id'] == int(item_id)].index[0]
    except IndexError:
        print(f"Error: ID {item_id} not found.")
        return []

    target_vec = embeddings[idx].reshape(1, -1)
    target_cat = df.iloc[idx]['category']
    target_cuisine = df.iloc[idx]['cuisine_type']
    target_res_id = df.iloc[idx]['restaurant_id']
    target_name = str(df.iloc[idx]['name']).lower()

    # --- CSV FALLBACK HACK ---
    # Just in case your CSV still says "General" for Momos, we forcefully correct it in memory
    if 'momo' in target_name or 'spring roll' in target_name:
        target_cuisine = 'Chinese'

    sim_scores = cosine_similarity(target_vec, embeddings).flatten()
    boosted_df = df.copy()
    boosted_df['similarity'] = sim_scores
    
    # 1. THE RESTAURANT LOCK
    boosted_df = boosted_df[boosted_df['restaurant_id'] == target_res_id]

    # 2. THE TITANIUM CUISINE SHIELD (Nukes Butter Chicken for Momos)
    cross_cuisine_mask = (boosted_df['cuisine_type'] != target_cuisine) & (~boosted_df['category'].isin(['Drink', 'Dessert']))
    boosted_df.loc[cross_cuisine_mask, 'similarity'] *= 0.0001 

    # 3. THE TEMPERATURE FILTER (Kills Masala Tea for Fast Food/Chinese)
    is_hot_drink = boosted_df['name'].str.lower().str.contains('tea|coffee')
    is_cold_drink = boosted_df['name'].str.lower().str.contains('coke|pepsi|sprite|soda|mojito|shake|lassi')
    
    if target_cuisine in ['Fast Food', 'Chinese'] or target_cat == 'Fast Food Main':
        boosted_df.loc[is_hot_drink, 'similarity'] *= 0.01   # Destroy hot drinks
        boosted_df.loc[is_cold_drink, 'similarity'] *= 2.0   # Boost sodas

    # 4. STRUCTURAL TAXONOMY MULTIPLIERS
    if target_cat == 'Wet Curry':
        boosted_df.loc[boosted_df['category'].isin(['Wet Curry', 'Dry Main']), 'similarity'] *= 0.05 
        boosted_df.loc[boosted_df['category'] == 'Bread', 'similarity'] *= 8.0 
        boosted_df.loc[boosted_df['category'] == 'Starter', 'similarity'] *= 2.0
        boosted_df.loc[boosted_df['category'] == 'Drink', 'similarity'] *= 1.5

    elif target_cat == 'Dry Main': 
        boosted_df.loc[boosted_df['category'].isin(['Wet Curry', 'Dry Main']), 'similarity'] *= 0.05
        boosted_df.loc[boosted_df['category'] == 'Side', 'similarity'] *= 5.0 
        boosted_df.loc[boosted_df['category'] == 'Starter', 'similarity'] *= 2.0
        boosted_df.loc[boosted_df['category'] == 'Drink', 'similarity'] *= 1.5

    elif target_cat == 'Fast Food Main': 
        boosted_df.loc[boosted_df['category'] == 'Fast Food Main', 'similarity'] *= 0.05
        boosted_df.loc[boosted_df['category'] == 'Side', 'similarity'] *= 6.0 
        boosted_df.loc[boosted_df['category'] == 'Drink', 'similarity'] *= 3.0

    elif target_cat == 'Bread':
        boosted_df.loc[boosted_df['category'] == 'Bread', 'similarity'] *= 0.05
        boosted_df.loc[boosted_df['category'] == 'Wet Curry', 'similarity'] *= 8.0 
        boosted_df.loc[boosted_df['category'] == 'Dry Main', 'similarity'] *= 0.1 
        boosted_df.loc[boosted_df['category'] == 'Starter', 'similarity'] *= 1.5

    elif target_cat == 'Starter':
        boosted_df.loc[boosted_df['category'] == 'Starter', 'similarity'] *= 0.05
        # Force Mains to the absolute top of the list over drinks
        boosted_df.loc[boosted_df['category'].isin(['Wet Curry', 'Dry Main', 'Fast Food Main']), 'similarity'] *= 10.0
        boosted_df.loc[boosted_df['category'] == 'Drink', 'similarity'] *= 3.0
        boosted_df.loc[boosted_df['category'] == 'Dessert', 'similarity'] *= 2.5

    elif target_cat == 'Dessert':
        boosted_df.loc[~boosted_df['category'].isin(['Dessert', 'Drink']), 'similarity'] *= 0.01

    if target_cat in ['Wet Curry', 'Dry Main', 'Fast Food Main', 'Bread']:
        boosted_df.loc[boosted_df['category'] == 'Dessert', 'similarity'] *= 0.3

    # Sort mathematically
    boosted_df = boosted_df.sort_values(by='similarity', ascending=False)
    
    # 5. BULLETPROOF DEDUPLICATION
    final_recs = []
    seen_names = {target_name.split('(')[0].strip()}
    
    for _, row in boosted_df.iterrows():
        clean_name = str(row['name']).split('(')[0].strip().lower()
        
        if int(float(row['item_id'])) == int(float(item_id)) or clean_name in seen_names:
            continue
            
        final_recs.append(row.to_dict())
        seen_names.add(clean_name)
        
        if len(final_recs) == top_n:
            break
            
    return final_recs