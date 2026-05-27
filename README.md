# Context-Aware Nutrition Copilot Assistant 🚀

A production-grade hackathon project that integrates a "Nutrition Copilot" directly into a food delivery experience, helping users make smarter, healthier choices in real-time.

## 🎯 Problem & Persona
**Persona:** Late-night college students (18–25) who frequently order fast food between 9 PM and 2 AM.  
**Problem:** Restrictive dieting apps are ignored. Students need gentle, non-judgmental nudges to choose healthier options or make slight upgrades to their typical junk food orders without feeling restricted.

## 💡 Solution Overview
The **Nutrition Copilot** is a real-time assistant layer that triggers when a user selects a food item. It calculates a dynamic `SmartScore` and uses AI to provide a personalized, context-aware insight, a healthier alternative, and a simple actionable upgrade.

## 🏗️ Architecture

```
[ Frontend (React/Vite) ] <--- JSON ---> [ Backend (FastAPI) ]
       |                                     |
    User UI                            Scoring Engine
 Copilot Modal                               |
                                    -------------------
                                    |                 |
                             [ Gemini API ]    [ Firebase DB ]
                             (Explanations)    (User History)
```

## 🧠 SmartScore Logic
The intelligence of the assistant relies on a structured formula calculated in `backend/scoring.py`:

**Formula:**
`SmartScore = BaseNutritionScore - TimePenalty + ProteinBonus - SugarPenalty - RepeatBehaviorPenalty`

- **TimePenalty:** Applied for high-calorie meals ordered after 10 PM.
- **ProteinBonus:** Added for meals high in satiating protein.
- **SugarPenalty:** Subtracted for high sugar content.
- **RepeatBehaviorPenalty:** Dynamically calculated by checking the user's past 7-day history in Firestore for repeated late-night junk food orders.

## ☁️ How Google Services Power This Project
1. **Gemini API:** Used to generate the 20-word non-judgmental explanations, specific better alternatives, and actionable upgrades. The prompt strictly enforces a JSON response schema for seamless UI integration.
2. **Firebase Firestore:** Simulates the backend database for user behavior. It stores past orders and is queried to generate the personalized "Behavior Insight" (e.g., *"You've ordered high-calorie meals 3 times this week after 10PM"*). 

*(Note: A local mock fallback is included in `firebase_service.py` to ensure the demo works out-of-the-box without credentials).*

## 🎥 Demo Flow
1. Open the React frontend.
2. Browse the food menu and click **Select Item** on a heavy meal like "Loaded Nachos" or "Double Bacon Cheeseburger".
3. The **Copilot Assistant** instantly appears.
4. Watch the loading state: "Analyzing your choice..." while the backend calculates the SmartScore and queries Gemini.
5. See the customized response containing the SmartScore, Behavior Insight, Explanation, Alternative, and Upgrade.
6. Click **Apply Upgrade** to simulate updating your order.

## 🚀 Setup Instructions

### Backend (Python/FastAPI)
1. `cd backend`
2. `pip install -r requirements.txt`
3. Export your Gemini API key: `export GEMINI_API_KEY="your_api_key"`
4. Run server: `uvicorn main:app --reload --port 8000`

### Frontend (React/Vite)
1. `cd frontend`
2. `npm install`
3. `npm run dev`

Open `http://localhost:5173` to interact with the demo.
