import os
import sys
import json

# Change directory to backend so imports work
sys.path.append("/Users/saara/amd-hackathon/backend")

from services.gemini_service import get_gemini_client, generate_copilot_response

def test_meal(name, cals):
    try:
        print(f"\n--- Testing {name} ({cals} kcal) ---")
        res = generate_copilot_response(
            food_name=name,
            score=45 if cals > 600 else 85,
            behavior_summary={
                "current_item": name,
                "current_category": "burger" if "Burger" in name else "pizza",
                "current_calories": cals,
                "avg_calories": 650,
                "calorie_diff": cals - 650,
                "is_above_avg": cals > 650,
                "is_repeat_item": False,
                "category_frequency": "low",
                "health_score_comparison": "similar",
                "time_context": "late night"
            },
            goals=["Weight Loss"],
            recent_upgrades=[],
            age="Young Adult",
            macros={"calories": cals, "protein": 30, "sugar": 5, "fat": 20, "fiber": 0, "calcium": 0, "iron": 0, "b12": 0, "carbs": 0}
        )
        print("Insight:", res.get("insight"))
    except Exception as e:
        print("Error:", e)

test_meal("Double Bacon Cheeseburger", 850)
test_meal("Veggie Pizza Slice", 450)
test_meal("Super Hefty Burrito", 950)
