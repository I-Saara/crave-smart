from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import datetime

from scoring import calculate_smart_score
from services.gemini_service import generate_copilot_response
from services.firebase_service import simulate_order, get_user_history_stats
from upgrade_engine import categorize_food

app = FastAPI(title="Context-Aware Nutrition Copilot API")

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FoodItemRequest(BaseModel):
    user_id: str
    food_name: str
    calories: int
    protein: int
    sugar: int
    fat: int
    fiber: float = 0.0
    calcium: float = 0.0
    iron: float = 0.0
    b12: float = 0.0
    carbs: float = 0.0
    order_time_iso: str  # e.g., "2026-05-06T23:00:00"
    goals: list[str] = []
    recent_upgrades: list[str] = []
    age: str = "Young Adult"

@app.get("/")
def read_root():
    return {"status": "Nutrition Copilot API is running"}

@app.post("/score-meal")
def score_meal(request: FoodItemRequest):
    # Parse time
    try:
        order_time = datetime.datetime.fromisoformat(request.order_time_iso)
    except ValueError:
        order_time = datetime.datetime.now()

    # 1. Fetch user stats from Firebase (mocked) to get repeat penalty
    user_stats = get_user_history_stats(request.user_id)
    
    # 2. Calculate SmartScore
    score_result = calculate_smart_score(
        calories=request.calories,
        protein=request.protein,
        sugar=request.sugar,
        order_time=order_time,
        late_night_junk_count=user_stats["late_night_junk_count"],
        goals=request.goals,
        age=request.age,
        macros={
            "fiber": request.fiber,
            "calcium": request.calcium,
            "iron": request.iron,
            "b12": request.b12,
            "carbs": request.carbs
        }
    )
    
    # 3. Generate Structured Behavior Summary
    avg_calories = 650
    food_category = categorize_food(request.food_name)
    frequent_category = "pizza" # Mock historical preference
    is_repeat_item = (user_stats["late_night_junk_count"] > 2)
    calorie_diff = request.calories - avg_calories
    is_above_avg = calorie_diff > 0
    
    health_score_comparison = "worse" if score_result["score"] < 50 else ("better" if score_result["score"] > 80 else "similar")
    category_frequency = "high" if food_category == frequent_category else "low"
        
    behavior_summary = {
        "current_item": request.food_name,
        "current_category": food_category,
        "current_calories": request.calories,
        "avg_calories": avg_calories,
        "calorie_diff": calorie_diff,
        "is_above_avg": is_above_avg,
        "is_repeat_item": is_repeat_item,
        "category_frequency": category_frequency,
        "health_score_comparison": health_score_comparison,
        "time_context": "late night" if order_time.hour >= 21 or order_time.hour < 4 else "daytime"
    }

    # 4. Get structured JSON from Gemini API
    gemini_data = generate_copilot_response(
        food_name=request.food_name,
        score=score_result["score"],
        behavior_summary=behavior_summary,
        goals=request.goals,
        recent_upgrades=request.recent_upgrades,
        age=request.age,
        macros={
            "calories": request.calories,
            "protein": request.protein,
            "sugar": request.sugar,
            "fat": request.fat,
            "fiber": request.fiber,
            "calcium": request.calcium,
            "iron": request.iron,
            "b12": request.b12,
            "carbs": request.carbs
        }
    )

    fallback_insight = ""
    if user_stats["late_night_junk_count"] > 1:
        fallback_insight = f"You've ordered high-calorie meals {user_stats['late_night_junk_count']} times this week after 10PM."
    elif score_result["score"] < 50:
        fallback_insight = "This is a bit heavy for this time of day."
    else:
        fallback_insight = "Great choice for your current context!"

    return {
        "smart_score": score_result["score"],
        "score_breakdown": score_result["breakdown"],
        "insight": gemini_data.get("insight", fallback_insight),
        "explanation": gemini_data.get("explanation", "It's okay, but you can do better!"),
        "alternative": gemini_data.get("alternative", "Try a grilled chicken salad."),
        "upgrade": gemini_data.get("upgrade", "Remove the extra cheese."),
        "nutrient_gain": gemini_data.get("nutrient_gain", {})
    }

class SimulateOrderRequest(BaseModel):
    user_id: str
    food_name: str
    calories: int
    time_iso: str

@app.post("/simulate-order")
def add_simulated_order(request: SimulateOrderRequest):
    simulate_order(
        user_id=request.user_id,
        food_name=request.food_name,
        calories=request.calories,
        time_iso=request.time_iso
    )
    return {"status": "success", "message": "Order simulated successfully"}

class CravingRequest(BaseModel):
    craving: str
    goals: list[str] = []
    age: str = "Young Adult"

from services.gemini_service import generate_craving_response

@app.post("/craving-suggestions")
def craving_suggestions(request: CravingRequest):
    result = generate_craving_response(
        craving=request.craving,
        goals=request.goals,
        age=request.age
    )
    return result

class CustomMealRequest(BaseModel):
    user_id: str
    query: str
    goals: list[str] = []
    age: str = "Young Adult"
    recent_upgrades: list[str] = []

from services.gemini_service import analyze_custom_food

@app.post("/analyze-custom-meal")
def analyze_custom_meal(request: CustomMealRequest):
    # 1. Use Gemini to estimate nutrition
    nutrition = analyze_custom_food(request.query)
    
    # 2. Score the meal
    order_time = datetime.datetime.now()
    user_stats = get_user_history_stats(request.user_id)
    
    score_result = calculate_smart_score(
        calories=nutrition["calories"],
        protein=nutrition["protein"],
        sugar=nutrition["sugar"],
        order_time=order_time,
        late_night_junk_count=user_stats["late_night_junk_count"],
        goals=request.goals,
        age=request.age,
        macros=nutrition
    )
    
    # 3. Generate Behavior Summary
    avg_calories = 650
    food_category = categorize_food(nutrition["food_name"])
    frequent_category = "pizza"
    is_repeat_item = False
    calorie_diff = nutrition["calories"] - avg_calories
    is_above_avg = calorie_diff > 0
    health_score_comparison = "worse" if score_result["score"] < 50 else ("better" if score_result["score"] > 80 else "similar")
    category_frequency = "high" if food_category == frequent_category else "low"
    
    behavior_summary = {
        "current_item": nutrition["food_name"],
        "current_category": food_category,
        "current_calories": nutrition["calories"],
        "avg_calories": avg_calories,
        "calorie_diff": calorie_diff,
        "is_above_avg": is_above_avg,
        "is_repeat_item": is_repeat_item,
        "category_frequency": category_frequency,
        "health_score_comparison": health_score_comparison,
        "time_context": "late night" if order_time.hour >= 21 or order_time.hour < 4 else "daytime"
    }

    # 4. Get structured JSON from Gemini API for upgrades
    gemini_data = generate_copilot_response(
        food_name=nutrition["food_name"],
        score=score_result["score"],
        behavior_summary=behavior_summary,
        goals=request.goals,
        recent_upgrades=request.recent_upgrades,
        age=request.age,
        macros=nutrition
    )

    return {
        "food_name": nutrition["food_name"],
        "calories": nutrition["calories"],
        "protein": nutrition["protein"],
        "sugar": nutrition["sugar"],
        "fat": nutrition["fat"],
        "carbs": nutrition["carbs"],
        "smart_score": score_result["score"],
        "score_breakdown": score_result["breakdown"],
        "insight": gemini_data.get("insight", "Great choice for your context!"),
        "explanation": gemini_data.get("explanation", "Estimated profile analyzed."),
        "alternative": gemini_data.get("alternative", "Try a healthier version."),
        "upgrade": gemini_data.get("upgrade", "Remove extra sauces."),
        "nutrient_gain": gemini_data.get("nutrient_gain", {})
    }
