import os
import json
from google import genai
from google.genai import types

def get_gemini_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Fallback for local testing if not in environment
        api_key = "AIzaSyB0oRtQXrj7AvQSbI52s-DEX8q194fO5Yw" 
    return genai.Client(api_key=api_key)

from upgrade_engine import get_heuristic_upgrade

def generate_copilot_response(food_name: str, score: int, behavior_summary: dict, goals: list[str], recent_upgrades: list[str], age: str, macros: dict):
    """
    Calls the Gemini API to get goal-driven, item-specific suggestions.
    """
    client = get_gemini_client()
    
    goals_str = ", ".join(goals) if goals else "None specific"
    
    # Get the heuristic fallback, exact math, and food features
    heuristic_upgrade_text, heuristic_gains, features, category = get_heuristic_upgrade(food_name, macros, goals, recent_upgrades)
    features_str = ", ".join(features)
    
    # Fallback if no API key is provided
    if not client:
        print("[GEMINI API CALL] Skipped due to missing GEMINI_API_KEY")
        return {
            "explanation": f"Score tailored for {goals_str}.",
            "alternative": "A balanced bowl or wrap.",
            "upgrade": heuristic_upgrade_text,
            "nutrient_gain": heuristic_gains
        }

    heuristic_gains_json = json.dumps(heuristic_gains)

    prompt = f"""
    You are a nutrition copilot formatting data calculated by our internal engine, and generating a dynamic behavior insight.
    The computed SmartScore for this meal is {score}/100.
    
    User Profile: Age {age}
    User Goals: {goals_str}
    
    BEHAVIOR SUMMARY:
    - Current item: {behavior_summary.get('current_item')}
    - Category: {behavior_summary.get('current_category')} (Frequency: {behavior_summary.get('category_frequency')})
    - Calories: {behavior_summary.get('current_calories')} kcal
    - User avg calories: {behavior_summary.get('avg_calories')} kcal
    - Comparison: {"higher" if behavior_summary.get('is_above_avg') else "lower"} (Diff: {behavior_summary.get('calorie_diff')} kcal)
    - Repeat item: {"yes" if behavior_summary.get('is_repeat_item') else "no"}
    - Health comparison: {behavior_summary.get('health_score_comparison')}
    - Time context: {behavior_summary.get('time_context')}
    
    ENGINE DECISION:
    - Upgrade Action: "{heuristic_upgrade_text}"
    - Nutrient Gains: {heuristic_gains_json}

    INSTRUCTION:
    1. Generate ONE short behavior insight (max 12 words). 
       - MUST reference current item OR its category.
       - MUST use comparison (higher/lower/similar).
       - DO NOT use generic phrases.
       - DO NOT mention time unless explicitly needed.
       - If the input changes, the output MUST change accordingly.
       - Each output must feel different from other items.
    2. Provide a short, friendly explanation of the score (max 20 words).
    3. Provide one specific better alternative dish aligned with the goals.
    4. You MUST return the EXACT "Upgrade Action" and "Nutrient Gains" provided in the ENGINE DECISION. DO NOT invent your own upgrade or alter the math. Just pass it through.

    You must output exactly and ONLY valid JSON matching this schema, without any markdown formatting:
    {{
        "insight": "string",
        "explanation": "string",
        "alternative": "string",
        "upgrade": "{heuristic_upgrade_text}",
        "nutrient_gain": {heuristic_gains_json}
    }}
    """
    
    print("\n--- DEBUG GEMINI INPUT ---")
    print(prompt)
    print("--------------------------\n")
    
    print(f"[GEMINI API CALL] Generating goal-based explanation for {food_name}")
    
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8
            ),
        )
        data = json.loads(response.text)
        print("\n--- DEBUG GEMINI OUTPUT ---")
        print(json.dumps(data, indent=2))
        print("---------------------------\n")
        return data
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        # CORE FIX: Dynamic heuristic fallback if AI fails or hits quota
        is_above = behavior_summary.get('is_above_avg', False)
        diff = abs(behavior_summary.get('calorie_diff', 0))
        category = behavior_summary.get('current_category', 'meal')
        
        if is_above:
            fallback_insight = f"This {food_name} is {diff}kcal higher than your usual {category} choice."
        else:
            fallback_insight = f"Great! This {food_name} is {diff}kcal lighter than your average {category}."

        alternative_map = {
            "burger": "A grilled chicken wrap or bunless patty.",
            "pizza": "A thin-crust veggie pizza or a salad.",
            "drink": "Sparkling water with lemon or green tea.",
            "dessert": "Greek yogurt with berries.",
            "meal": "A balanced protein bowl."
        }
        fallback_alt = alternative_map.get(category, "A balanced protein bowl.")

        return {
            "insight": fallback_insight,
            "explanation": f"Based on your profile, this {category} is being analyzed against your patterns.",
            "alternative": fallback_alt,
            "upgrade": heuristic_upgrade_text,
            "nutrient_gain": heuristic_gains
        }

CRAVING_CATEGORIES = {
    "chocolate": "sweet",
    "ice cream": "sweet",
    "chips": "salty_crunchy",
    "fries": "salty_crunchy",
    "soda": "sweet_drink",
    "burger": "savory_heavy",
    "candy": "sweet",
    "pizza": "savory_heavy",
    "cookies": "sweet"
}

CRAVING_STRICT_MAPPING = {
    "sweet": ["Dark chocolate squares", "Cocoa-dusted almonds", "Greek yogurt with fruit"],
    "salty_crunchy": ["Roasted makhana (fox nuts)", "Air-popped popcorn", "Baked chickpea snacks"],
    "sweet_drink": ["Sparkling water with lemon", "Cold brewed fruit tea", "Kombucha"],
    "savory_heavy": ["Grilled chicken lettuce wrap", "Turkey and cheese roll-ups", "Baked sweet potato wedges"],
    "general_craving": ["A handful of mixed nuts", "Apple slices with peanut butter", "A protein shake"]
}

def categorize_craving(craving: str):
    craving_lower = craving.lower()
    for key, category in CRAVING_CATEGORIES.items():
        if key in craving_lower:
            return category
    return "general_craving"

def generate_craving_response(craving: str, goals: list[str], age: str):
    """
    Handles Cravings Assistant mode by suggesting 3-5 healthier alternatives.
    """
    client = get_gemini_client()
    goals_str = ", ".join(goals) if goals else "None specific"
    category = categorize_craving(craving)
    strict_alts = CRAVING_STRICT_MAPPING.get(category, CRAVING_STRICT_MAPPING["general_craving"])
    
    if not client:
        print("[GEMINI API CALL] Skipped due to missing GEMINI_API_KEY")
        return {
            "category": category,
            "alternatives": strict_alts,
            "reason": "These are strictly curated to satisfy your craving safely."
        }
        
    prompt = f"""
    You are a helpful nutrition assistant.
    User Profile: Age {age}
    User Goals: {goals_str}
    The user is currently craving: "{craving}"
    Craving Category: {category}
    
    Our backend has locked in these EXACT alternatives for this category: {strict_alts}

    INSTRUCTION:
    Write a short, encouraging reason (1 sentence) explaining why these alternatives fit their goals and satisfy the {category} craving. 
    You MUST output the EXACT alternatives provided by the backend. Do not invent new ones.

    You must output exactly and ONLY valid JSON matching this schema, without any markdown formatting:
    {{
        "category": "{category}",
        "alternatives": {strict_alts},
        "reason": "short explanation of why these fit their goals"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8
            ),
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        return {
            "category": category,
            "alternatives": ["Dark chocolate", "Greek yogurt with honey"],
            "reason": "These are great satisfying alternatives."
        }

def analyze_custom_food(food_query: str):
    """
    Uses Gemini to estimate nutrition for a custom food query.
    """
    client = get_gemini_client()
    if not client:
        # Fallback if no API key
        return {
            "food_name": food_query,
            "calories": 500,
            "protein": 10,
            "sugar": 10,
            "fat": 20,
            "carbs": 50,
            "fiber": 1.0,
            "calcium": 50.0,
            "iron": 1.0,
            "b12": 0.1
        }

    prompt = f"""
    Estimate the nutritional profile for this food item: "{food_query}".
    Be realistic and provide standard serving size values.
    
    You must output exactly and ONLY valid JSON matching this schema, without any markdown formatting:
    {{
        "food_name": "string",
        "calories": integer,
        "protein": integer,
        "sugar": integer,
        "fat": integer,
        "carbs": integer,
        "fiber": float,
        "calcium": float,
        "iron": float,
        "b12": float
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.3
            ),
        )
        data = json.loads(response.text)
        return data
    except Exception as e:
        print(f"[GEMINI CUSTOM ERROR] {e}")
        # Realistic fallback if Gemini fails for custom meal
        is_junk = any(x in food_query.lower() for x in ["shake", "burger", "pizza", "fry", "cake"])
        return {
            "food_name": food_query.title(),
            "calories": 650 if is_junk else 350,
            "protein": 15 if is_junk else 20,
            "sugar": 30 if is_junk else 5,
            "fat": 25 if is_junk else 10,
            "carbs": 60 if is_junk else 30,
            "fiber": 1.0,
            "calcium": 50.0,
            "iron": 1.0,
            "b12": 0.1
        }
