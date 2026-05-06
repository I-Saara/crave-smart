import os
import datetime

# Mock Database for User History (In-memory fallback)
MOCK_DB = {
    "user_123": [
        {"food_name": "Loaded Nachos", "calories": 900, "time_iso": "2026-05-04T23:30:00"},
        {"food_name": "Double Cheeseburger", "calories": 850, "time_iso": "2026-05-05T01:15:00"},
    ]
}

def get_firebase_db():
    """
    In a real scenario, this initializes firebase_admin and returns firestore.client().
    For the hackathon demo, we will use an in-memory mock if credentials are missing.
    """
    if os.environ.get("FIREBASE_CREDENTIALS"):
        # Real initialization would happen here
        # import firebase_admin
        # from firebase_admin import credentials, firestore
        # cred = credentials.Certificate(os.environ.get("FIREBASE_CREDENTIALS"))
        # firebase_admin.initialize_app(cred)
        # return firestore.client()
        pass
    return None

def simulate_order(user_id: str, food_name: str, calories: int, time_iso: str):
    """
    Simulates placing an order and stores it in the user's history.
    """
    db = get_firebase_db()
    if db:
        print(f"[FIREBASE] Inserting order for {user_id} into Firestore")
        # db.collection("users").document(user_id).collection("history").add({...})
    else:
        print(f"[FIREBASE MOCK] Inserting order for {user_id} into mock DB")
        if user_id not in MOCK_DB:
            MOCK_DB[user_id] = []
        MOCK_DB[user_id].append({
            "food_name": food_name,
            "calories": calories,
            "time_iso": time_iso
        })

def get_user_history_stats(user_id: str):
    """
    Retrieves user history and calculates late-night junk count.
    """
    db = get_firebase_db()
    history = []
    
    if db:
        print(f"[FIREBASE] Fetching history for {user_id} from Firestore")
        # docs = db.collection("users").document(user_id).collection("history").stream()
        # history = [doc.to_dict() for doc in docs]
    else:
        print(f"[FIREBASE MOCK] Fetching history for {user_id} from mock DB")
        history = MOCK_DB.get(user_id, [])

    # Calculate how many late-night high-calorie meals this week
    late_night_junk_count = 0
    now = datetime.datetime.now()
    
    for order in history:
        try:
            order_time = datetime.datetime.fromisoformat(order["time_iso"])
            # Check if within last 7 days
            if (now - order_time).days <= 7:
                hour = order_time.hour
                is_late_night = (hour >= 22 or hour <= 4)
                if is_late_night and order.get("calories", 0) > 500:
                    late_night_junk_count += 1
        except ValueError:
            continue
            
    return {
        "late_night_junk_count": late_night_junk_count,
        "total_orders": len(history)
    }
