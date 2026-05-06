import hashlib

# Realistic Nutrient Data for Upgrades (USDA-equivalent mock data)
REALISTIC_INGREDIENTS_DB = {
    "grilled_chicken": { "text": "Add a side of grilled chicken", "protein": 25, "calories": 150 },
    "paneer": { "text": "Add a side of paneer", "protein": 18, "calcium": 200, "calories": 250 },
    "boiled_egg": { "text": "Add a boiled egg", "protein": 6, "b12": 0.6, "calories": 70 },
    "spinach": { "text": "Add a spinach salad", "iron": 2.7, "fiber": 2, "calories": 10 },
    "milk": { "text": "Pair with a glass of milk", "calcium": 300, "protein": 8, "calories": 150 },
    "nuts": { "text": "Add a handful of mixed nuts", "fiber": 3, "fat": 15, "calories": 170 },
    "water": { "text": "Replace the sugary drink with water", "sugar": -30, "calories": -140 },
    "veggies": { "text": "Add a side of mixed veggies", "fiber": 5, "calories": 45 },
    "thin_crust": { "text": "Switch to a thin crust", "carbs": -30, "calories": -150 },
    "chicken_topping": { "text": "Add a grilled chicken topping", "protein": 20, "calories": 120 },
    "grilled_patty": { "text": "Switch to a grilled chicken patty", "fat": -15, "calories": -120 },
    "remove_cheese": { "text": "Remove the extra cheese", "fat": -12, "calories": -100 }
}

# Categorize food based on name
def categorize_food(food_name: str) -> str:
    name_lower = food_name.lower()
    if "burger" in name_lower or "sandwich" in name_lower: return "burger"
    if "pizza" in name_lower: return "pizza"
    if "wrap" in name_lower or "roll" in name_lower: return "wrap"
    if "salad" in name_lower: return "salad"
    if "shake" in name_lower or "drink" in name_lower or "soda" in name_lower: return "drink"
    return "snack"

# Context-aware upgrade rules based on category and goal
CATEGORY_UPGRADE_RULES = {
    "burger": {
        "High Protein": ["grilled_patty", "boiled_egg"],
        "Weight Loss": ["grilled_patty", "remove_cheese"],
        "Balanced Diet": ["veggies"],
        "Low Carb": ["remove_cheese", "veggies"],
        "Heart Healthy": ["veggies"],
        "Vitamin B12 Rich": ["boiled_egg"],
        "High Fiber": ["veggies"]
    },
    "pizza": {
        "High Protein": ["chicken_topping"],
        "Weight Loss": ["thin_crust", "remove_cheese"],
        "High Fiber": ["veggies"],
        "Low Carb": ["thin_crust", "remove_cheese"],
        "Heart Healthy": ["veggies"],
        "High Calcium": ["paneer"]
    },
    "wrap": {
        "High Protein": ["grilled_chicken", "paneer", "boiled_egg"],
        "High Iron": ["spinach"],
        "Balanced Diet": ["veggies"],
        "Low Carb": ["spinach", "veggies"],
        "High Fiber": ["spinach", "veggies"],
        "Vitamin B12 Rich": ["boiled_egg"]
    },
    "drink": {
        "Low Sugar": ["water"],
        "High Calcium": ["milk"],
        "Weight Loss": ["water"],
        "Heart Healthy": ["water"]
    },
    "salad": {
        "High Protein": ["grilled_chicken", "boiled_egg"],
        "High Calcium": ["paneer"],
        "Balanced Diet": ["nuts"],
        "High Iron": ["spinach"],
        "Vitamin B12 Rich": ["boiled_egg"],
        "High Fiber": ["nuts", "veggies"]
    },
    "snack": {
        "High Protein": ["boiled_egg", "nuts"],
        "High Fiber": ["veggies", "nuts"],
        "Weight Loss": ["veggies"],
        "High Iron": ["spinach"],
        "Low Carb": ["nuts"],
        "Vitamin B12 Rich": ["boiled_egg"]
    }
}

def classify_food(macros: dict):
    features = []
    if macros.get("calories", 0) > 600: features.append("high_calorie")
    if macros.get("protein", 0) < 15: features.append("low_protein")
    if macros.get("sugar", 0) > 10: features.append("high_sugar")
    if macros.get("fat", 0) > 30: features.append("high_fat")
    return features

def get_heuristic_upgrade(food_name: str, macros: dict, goals: list[str], recent_upgrades: list[str]):
    category = categorize_food(food_name)
    features = classify_food(macros)
    
    primary_goal = goals[0] if goals else "Balanced Diet"
    allowed_ingredients = CATEGORY_UPGRADE_RULES.get(category, {}).get(primary_goal, [])
    
    # Fallbacks if no exact goal match
    if not allowed_ingredients:
        allowed_ingredients = CATEGORY_UPGRADE_RULES.get(category, {}).get("Balanced Diet", ["veggies"])
        
    # Pick deterministically avoiding recents
    base_hash = int(hashlib.md5(food_name.encode('utf-8')).hexdigest(), 16)
    selected_key = None
    
    for i in range(len(allowed_ingredients)):
        idx = (base_hash + i) % len(allowed_ingredients)
        candidate_key = allowed_ingredients[idx]
        candidate_text = REALISTIC_INGREDIENTS_DB[candidate_key]["text"]
        if candidate_text not in recent_upgrades:
            selected_key = candidate_key
            break
            
    if not selected_key:
        selected_key = allowed_ingredients[0]

    selected_data = REALISTIC_INGREDIENTS_DB[selected_key]
    upgrade_text = selected_data["text"]
    
    # Calculate exact mathematical gains
    nutrient_gains = {}
    for nutrient, change in selected_data.items():
        if nutrient != "text":
            original_value = float(macros.get(nutrient, 0))
            new_total = original_value + change
            
            unit = "g"
            if nutrient in ["calories"]: unit = "kcal"
            if nutrient in ["calcium", "iron"]: unit = "mg"
            if nutrient in ["b12"]: unit = "mcg"
            
            sign = "+" if change > 0 else ""
            nutrient_gains[nutrient] = {
                "change_text": f"{sign}{change}{unit} {nutrient}",
                "new_total": f"{new_total}{unit}"
            }
            
    return upgrade_text, nutrient_gains, features, category
