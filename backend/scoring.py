import datetime

def calculate_smart_score(calories: int, protein: int, sugar: int, order_time: datetime.datetime, late_night_junk_count: int, goals: list[str] = [], age: str = "Young Adult", macros: dict = {}):
    """
    Calculates the SmartScore (0-100) based on heuristics, user goals, and age.
    Formula: Base - TimePenalty + ProteinBonus - SugarPenalty - RepeatBehaviorPenalty + NutrientBoosts
    """
    # Dynamic Goal Weights based on Age and Goals
    w_cal_penalty = 1.0
    w_protein_bonus = 1.0
    w_sugar_penalty = 1.0

    # Age-based Multipliers
    if age == "Teen":
        w_cal_penalty = 0.7  # Higher calorie tolerance
        w_protein_bonus = 1.5 # Emphasize growth
    elif age == "Adult":
        w_cal_penalty = 1.2
        w_sugar_penalty = 1.2
    elif age == "Senior":
        w_cal_penalty = 1.5
        w_sugar_penalty = 1.5
    
    if "Weight Loss" in goals:
        w_cal_penalty = 1.5
    if "Muscle Gain" in goals:
        w_protein_bonus = 2.0
        w_cal_penalty = 0.5 # Less penalty for high calories if protein is the goal
    if "Weight Gain" in goals:
        w_cal_penalty = 0.0 # No penalty for calories
    if "Low Sugar" in goals:
        w_sugar_penalty = 2.0

    # 1. Base Nutrition Score
    base_score = 80
    if calories > 800:
        base_score -= (20 * w_cal_penalty)
    elif calories > 600:
        base_score -= (10 * w_cal_penalty)
    elif calories < 300:
        if "Weight Loss" in goals:
            base_score += 10 # Reward low calories
        else:
            base_score -= 10 # Might not be satiating otherwise
        
    # 2. Time Penalty (after 10 PM until 4 AM)
    time_penalty = 0
    hour = order_time.hour
    is_late_night = (hour >= 22 or hour <= 4)
    if is_late_night and calories > 500:
        time_penalty = 15 * w_cal_penalty
        
    # 3. Protein Bonus
    protein_bonus = 0
    if protein >= 20:
        protein_bonus = 10 * w_protein_bonus
    elif protein >= 30:
        protein_bonus = 15 * w_protein_bonus
        
    # 4. Sugar Penalty
    sugar_penalty = 0
    if sugar > 15:
        sugar_penalty = 10 * w_sugar_penalty
    elif sugar > 30:
        sugar_penalty = 20 * w_sugar_penalty
        
    # 5. Repeat Behavior Penalty
    repeat_penalty = 0
    if late_night_junk_count >= 2:
        repeat_penalty = 10
    elif late_night_junk_count >= 4:
        repeat_penalty = 20
        
    # 6. Nutrient Boosts
    nutrient_boost = 0
    if "High Fiber" in goals and macros.get("fiber", 0) >= 5:
        nutrient_boost += 10
    if "High Calcium" in goals and macros.get("calcium", 0) >= 200:
        nutrient_boost += 10
    if "High Iron" in goals and macros.get("iron", 0) >= 3:
        nutrient_boost += 10
    if "Vitamin B12 Rich" in goals and macros.get("b12", 0) >= 1:
        nutrient_boost += 10
    if "Low Carb" in goals and macros.get("carbs", 0) > 40:
        nutrient_boost -= 15 # Actually a penalty
    if "Heart Healthy" in goals and macros.get("fiber", 0) >= 4:
        nutrient_boost += 10
        
    if age == "Senior" and macros.get("calcium", 0) >= 200:
        nutrient_boost += 15 # Extra boost for seniors
        
    # Calculate Final Score
    final_score = base_score - time_penalty + protein_bonus - sugar_penalty - repeat_penalty + nutrient_boost
    
    # Clamp between 0 and 100
    final_score = max(0, min(100, int(final_score)))
    
    return {
        "score": final_score,
        "breakdown": {
            "base": int(base_score),
            "time_penalty": -int(time_penalty),
            "protein_bonus": f"+{int(protein_bonus)}",
            "sugar_penalty": -int(sugar_penalty),
            "repeat_penalty": -int(repeat_penalty),
            "nutrient_boost": int(nutrient_boost)
        }
    }
