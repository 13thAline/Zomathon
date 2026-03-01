import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

print("Loading the Master Catalog")
df = pd.read_csv("master_items.csv")

# Pre-compute menus by restaurant and exact category
restaurants = df.groupby('restaurant_id')
res_menus = {}

for res_id, group in restaurants:
    res_menus[res_id] = {cat: group[group['category'] == cat]['item_id'].tolist() for cat in group['category'].unique()}
    res_menus[res_id]['all'] = group['item_id'].tolist()

res_ids = list(res_menus.keys())

#Personas To simulate the user behavior (Explained in the docs on how we decided the values)
personas = [
    {
        "name": "The Curry Feast",
        "weight": 0.25,
        "cart_rules": [
            {"cat": "Wet Curry", "prob": 1.0}, 
            {"cat": "Bread", "prob": 1.0},      
            {"cat": "Starter", "prob": 0.5}, 
            {"cat": "Drink", "prob": 0.4}
        ]
    },
    {
        "name": "The Biryani/Thali Diner",
        "weight": 0.20,
        "cart_rules": [
            {"cat": "Dry Main", "prob": 1.0}, 
            {"cat": "Side", "prob": 0.8},       
            {"cat": "Drink", "prob": 0.5}
        ]
    },
    {
        "name": "The Fast Food Junkie",
        "weight": 0.25,
        "cart_rules": [
            {"cat": "Fast Food Main", "prob": 1.0}, 
            {"cat": "Side", "prob": 0.9},       
            {"cat": "Drink", "prob": 0.8}
        ]
    },
    {
        "name": "The Chinese Takeout",
        "weight": 0.15,
        "cart_rules": [
            {"cat": "Dry Main", "prob": 0.7},   
            {"cat": "Wet Curry", "prob": 0.5},  
            {"cat": "Starter", "prob": 0.6}     
        ]
    },
    {
        "name": "The Sweet Tooth & Snack",
        "weight": 0.15,
        "cart_rules": [
            {"cat": "Dessert", "prob": 0.8}, 
            {"cat": "Side", "prob": 0.4}, 
            {"cat": "Drink", "prob": 0.5}
        ]
    }
]

users = [f"U_{i}" for i in range(1, 3501)]
persona_weights = [p["weight"] for p in personas]

events = []
current_time = datetime(2025, 12, 1, 12, 0)

print("Simulating 100,000 Highly Structured Sessions")
for session_num in range(100000):
    user_id = random.choice(users)
    persona = random.choices(personas, weights=persona_weights, k=1)[0]
    
    # Pick a random restaurant
    res_id = random.choice(res_ids)
    menu = res_menus[res_id]
    
    cart = []
    
    # Build the cart based on the structural rules
    for rule in persona["cart_rules"]:
        category = rule["cat"]
        if random.random() < rule["prob"] and category in menu and menu[category]:
            cart.append(random.choice(menu[category]))
            
    # Fallback if the restaurant didn't have the specific categories for that persona
    if not cart:
        cart.append(random.choice(menu['all']))
        
    session_id = f"sess_{user_id}_{session_num}"
    current_time += timedelta(minutes=random.randint(5, 60))
    day_of_week = current_time.strftime('%A')
    
    # Generate the funnel events
    for item in set(cart):
        events.append([user_id, item, res_id, "view", current_time, session_id, day_of_week])
        current_time += timedelta(seconds=random.randint(5, 15))
        
        if random.random() < 0.85: 
            events.append([user_id, item, res_id, "add_to_cart", current_time, session_id, day_of_week])
            current_time += timedelta(seconds=random.randint(10, 30))
            
            if random.random() < 0.70: 
                events.append([user_id, item, res_id, "order", current_time, session_id, day_of_week])

print("Exporting to interactions.csv")
df_events = pd.DataFrame(events, columns=["user_id", "item_id", "restaurant_id", "interaction_type", "timestamp", "session_id", "day_of_week"])
df_events = df_events.sort_values("timestamp")
df_events.to_csv("interactions.csv", index=False)
print(f"SUCCESS. Generated {len(df_events)} interaction rows.")