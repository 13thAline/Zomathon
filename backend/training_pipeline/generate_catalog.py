import pandas as pd
import numpy as np
import random

print("Loading the clean items dataset to get the restaurant data")
old_df = pd.read_csv("clean_items.csv") #The Dataset we used to generate embeddings which failed miserably due to the dat being not upto the mark
restaurants = old_df[['restaurant_id', 'restaurant_name', 'city', 'locality']].drop_duplicates()

# Confirm that there are at least 100 restaurants
restaurants = restaurants.head(100).to_dict('records')

print(f"Extracted {len(restaurants)} real restaurants.")

#Categorizing data for better model understanding
base_items = [
    # FAST FOOD MAINS
    {"name": "Chicken Zinger Burger", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 0, "base_price": 250},
    {"name": "Veggie Supreme Burger", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 1, "base_price": 180},
    {"name": "Double Cheese Margherita Pizza", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 1, "base_price": 350},
    {"name": "Pepperoni Pizza", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 0, "base_price": 450},
    {"name": "Farmhouse Pizza", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 1, "base_price": 380},
    {"name": "Chicken Tikka Sub Wrap", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 0, "base_price": 210},
    {"name": "Paneer Tikka Wrap", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 1, "base_price": 190},
    {"name": "White Sauce Penne Pasta", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 1, "base_price": 280},
    {"name": "Arrabiata Chicken Pasta", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 0, "base_price": 320},
    {"name": "Crispy Chicken Hotdog", "cuisine": "Fast Food", "cat": "Fast Food Main", "veg": 0, "base_price": 150},
    
    # NORTH INDIAN WET CURRIES
    {"name": "Butter Chicken", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 0, "base_price": 380},
    {"name": "Paneer Butter Masala", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 1, "base_price": 320},
    {"name": "Dal Makhani", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 1, "base_price": 240},
    {"name": "Chicken Tikka Masala", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 0, "base_price": 360},
    {"name": "Kadai Paneer", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 1, "base_price": 310},
    {"name": "Mutton Rogan Josh", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 0, "base_price": 450},
    {"name": "Chole Masala", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 1, "base_price": 220},
    {"name": "Palak Paneer", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 1, "base_price": 290},
    {"name": "Egg Curry", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 0, "base_price": 210},
    {"name": "Malai Kofta", "cuisine": "North Indian", "cat": "Wet Curry", "veg": 1, "base_price": 330},

    # NORTH INDIAN DRY MAINS
    {"name": "Hyderabadi Chicken Biryani", "cuisine": "North Indian", "cat": "Dry Main", "veg": 0, "base_price": 350},
    {"name": "Veg Dum Biryani", "cuisine": "North Indian", "cat": "Dry Main", "veg": 1, "base_price": 280},
    {"name": "Mutton Biryani", "cuisine": "North Indian", "cat": "Dry Main", "veg": 0, "base_price": 420},
    {"name": "Special North Indian Thali", "cuisine": "North Indian", "cat": "Dry Main", "veg": 1, "base_price": 300},
    {"name": "Punjabi Non-Veg Thali", "cuisine": "North Indian", "cat": "Dry Main", "veg": 0, "base_price": 380},

    # CHINESE DRY MAINS
    {"name": "Veg Hakka Noodles", "cuisine": "Chinese", "cat": "Dry Main", "veg": 1, "base_price": 190},
    {"name": "Chicken Schezwan Noodles", "cuisine": "Chinese", "cat": "Dry Main", "veg": 0, "base_price": 230},
    {"name": "Veg Fried Rice", "cuisine": "Chinese", "cat": "Dry Main", "veg": 1, "base_price": 180},
    {"name": "Egg Fried Rice", "cuisine": "Chinese", "cat": "Dry Main", "veg": 0, "base_price": 200},
    {"name": "Chicken Fried Rice", "cuisine": "Chinese", "cat": "Dry Main", "veg": 0, "base_price": 240},

    # CHINESE WET CURRIES
    {"name": "Veg Manchurian Gravy", "cuisine": "Chinese", "cat": "Wet Curry", "veg": 1, "base_price": 220},
    {"name": "Chilli Chicken Gravy", "cuisine": "Chinese", "cat": "Wet Curry", "veg": 0, "base_price": 280},
    {"name": "Paneer Chilli Gravy", "cuisine": "Chinese", "cat": "Wet Curry", "veg": 1, "base_price": 260},

    # BREADS (Strictly Indian)
    {"name": "Butter Naan", "cuisine": "North Indian", "cat": "Bread", "veg": 1, "base_price": 60},
    {"name": "Garlic Naan", "cuisine": "North Indian", "cat": "Bread", "veg": 1, "base_price": 75},
    {"name": "Tandoori Roti", "cuisine": "North Indian", "cat": "Bread", "veg": 1, "base_price": 30},
    {"name": "Lachha Paratha", "cuisine": "North Indian", "cat": "Bread", "veg": 1, "base_price": 50},
    {"name": "Aloo Stuffed Kulcha", "cuisine": "North Indian", "cat": "Bread", "veg": 1, "base_price": 80},
    {"name": "Bhature (2 pcs)", "cuisine": "North Indian", "cat": "Bread", "veg": 1, "base_price": 90},

    # STARTERS (Mixed)
    {"name": "Chicken Steam Momos", "cuisine": "Chinese", "cat": "Starter", "veg": 0, "base_price": 150},
    {"name": "Veg Fried Momos", "cuisine": "Chinese", "cat": "Starter", "veg": 1, "base_price": 130},
    {"name": "Chicken Spring Rolls", "cuisine": "Chinese", "cat": "Starter", "veg": 0, "base_price": 180},
    {"name": "Veg Spring Rolls", "cuisine": "Chinese", "cat": "Starter", "veg": 1, "base_price": 150},
    {"name": "Honey Chilli Potato", "cuisine": "Chinese", "cat": "Starter", "veg": 1, "base_price": 190},
    {"name": "Chicken Tikka Kebab", "cuisine": "North Indian", "cat": "Starter", "veg": 0, "base_price": 320},
    {"name": "Paneer Tikka", "cuisine": "North Indian", "cat": "Starter", "veg": 1, "base_price": 280},
    {"name": "Hara Bhara Kabab", "cuisine": "North Indian", "cat": "Starter", "veg": 1, "base_price": 240},
    {"name": "Mutton Seekh Kebab", "cuisine": "North Indian", "cat": "Starter", "veg": 0, "base_price": 380},
    {"name": "Chicken Wings (Hot & Spicy)", "cuisine": "Fast Food", "cat": "Starter", "veg": 0, "base_price": 220},
    {"name": "Crispy Chicken Nuggets", "cuisine": "Fast Food", "cat": "Starter", "veg": 0, "base_price": 180},
    {"name": "Jalapeno Cheese Poppers", "cuisine": "Fast Food", "cat": "Starter", "veg": 1, "base_price": 190},

    # SIDES (Mixed)
    {"name": "Salted French Fries", "cuisine": "Fast Food", "cat": "Side", "veg": 1, "base_price": 110},
    {"name": "Peri Peri Fries", "cuisine": "Fast Food", "cat": "Side", "veg": 1, "base_price": 130},
    {"name": "Cheesy Potato Wedges", "cuisine": "Fast Food", "cat": "Side", "veg": 1, "base_price": 150},
    {"name": "Garlic Bread Sticks", "cuisine": "Fast Food", "cat": "Side", "veg": 1, "base_price": 140},
    {"name": "Cheese Dip", "cuisine": "Fast Food", "cat": "Side", "veg": 1, "base_price": 30},
    {"name": "Boondi Raita", "cuisine": "North Indian", "cat": "Side", "veg": 1, "base_price": 80},
    {"name": "Mixed Veg Raita", "cuisine": "North Indian", "cat": "Side", "veg": 1, "base_price": 90},
    {"name": "Roasted Masala Papad", "cuisine": "North Indian", "cat": "Side", "veg": 1, "base_price": 40},
    {"name": "Mint Chutney", "cuisine": "North Indian", "cat": "Side", "veg": 1, "base_price": 20},
    {"name": "Schezwan Sauce Dip", "cuisine": "Chinese", "cat": "Side", "veg": 1, "base_price": 30},

    # DESSERTS
    {"name": "Chocolate Brownie with Ice Cream", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 220},
    {"name": "Choco Lava Cake", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 130},
    {"name": "New York Cheesecake", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 280},
    {"name": "Tiramisu Cup", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 250},
    {"name": "Gulab Jamun (2 pcs)", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 90},
    {"name": "Rasmalai (2 pcs)", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 120},
    {"name": "Gajar Ka Halwa", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 150},
    {"name": "Moong Dal Halwa", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 160},
    {"name": "Vanilla Ice Cream Scoop", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 80},
    {"name": "Death by Chocolate Sundae", "cuisine": "Dessert", "cat": "Dessert", "veg": 1, "base_price": 260},

    # DRINKS (Cold)
    {"name": "Coca-Cola (330ml)", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 60},
    {"name": "Sprite (330ml)", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 60},
    {"name": "Thums Up (330ml)", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 60},
    {"name": "Virgin Mojito", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 150},
    {"name": "Fresh Lime Soda", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 110},
    {"name": "Sweet Lassi", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 90},
    {"name": "Mango Shake", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 140},
    {"name": "Cold Coffee with Ice Cream", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 180},
    {"name": "Iced Lemon Peach Tea", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 160},
    {"name": "Mineral Water (1L)", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 40},

    # DRINKS (Hot)
    {"name": "Masala Tea", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 50},
    {"name": "Hot Filter Coffee", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 70},
    {"name": "Cappuccino", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 160},
    {"name": "Hot Chocolate", "cuisine": "Beverage", "cat": "Drink", "veg": 1, "base_price": 190}
]

print("Distributing Items via Menu Specialization")
final_menu_rows = []
item_id_counter = 1

# Culinary Profiles dictate what a restaurant is allowed to sell
culinary_profiles = [
    ["Fast Food", "Beverage", "Dessert"], # Fast food restaurants can only sell fast food items
    ["North Indian", "Beverage", "Dessert"], # North Indian restaurants can only sell north indian items
    ["Chinese", "Beverage"], # Chinese restaurants can only sell chinese items
    ["North Indian", "Chinese", "Beverage", "Dessert"], # Generic multi-cuisine
    ["Fast Food", "Chinese", "Beverage"] # fast food and chinese restaurants can sell fast food and chinese items
]

for res in restaurants:
    profile = random.choice(culinary_profiles)
    
    for item in base_items:
        if item["cuisine"] in profile:
            if random.random() < 0.80:
                # Add 5% to 15% random price fluctuation per restaurant
                price_variance = random.uniform(0.95, 1.15)
                final_price = int(item["base_price"] * price_variance)
                
                # Format the ML description string perfectly
                diet = "Vegetarian" if item["veg"] == 1 else "Non-Vegetarian"
                desc = f"{item['name']}. A {diet} {item['cuisine']} {item['cat']}."
                
                final_menu_rows.append({
                    "item_id": item_id_counter,
                    "restaurant_id": res["restaurant_id"],
                    "restaurant_name": res["restaurant_name"],
                    "city": res["city"],
                    "locality": res["locality"],
                    "cuisine_type": item["cuisine"],
                    "name": item["name"],
                    "description": desc,
                    "price": final_price,
                    "category": item["cat"],
                    "is_veg": item["veg"]
                })
                item_id_counter += 1

final_df = pd.DataFrame(final_menu_rows)

print("3. Exporting the Master Catalog...")
final_df.to_csv("master_items.csv", index=False)
print(f"SUCCESS. Generated {len(final_df)} highly structured menu items across {len(restaurants)} restaurants.")
print("Saved as 'master_items.csv'")