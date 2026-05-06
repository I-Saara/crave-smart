import React, { useState } from 'react';
import FoodMenu from './components/FoodMenu';
import CopilotModal from './components/CopilotModal';
import SaladBowlBuilder from './components/SaladBowlBuilder';
import CravingsModal from './components/CravingsModal';

function App() {
  const [selectedGoals, setSelectedGoals] = useState(null);
  const [userAge, setUserAge] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [upgradedItems, setUpgradedItems] = useState({});
  const [recentUpgrades, setRecentUpgrades] = useState([]);
  const [showCravings, setShowCravings] = useState(false);
  const [customMealQuery, setCustomMealQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSaveGoals = (data) => {
    setSelectedGoals(data.goals);
    setUserAge(data.age);
  };

  const handleSelectItem = (item) => {
    setSelectedItem(item);
  };

  const handleCloseModal = () => {
    setSelectedItem(null);
  };

  const handleApplyUpgrade = (upgradeText) => {
    setUpgradedItems({
      ...upgradedItems,
      [selectedItem.id]: upgradeText
    });
    setSelectedItem(null);
    alert(`Upgrade applied: ${upgradeText}`);
  };

  const handleUpgradeShown = (upgradeText) => {
    if (upgradeText && !recentUpgrades.includes(upgradeText)) {
      setRecentUpgrades((prev) => [upgradeText, ...prev].slice(0, 5));
    }
  };

  const handleAnalyzeCustomMeal = async () => {
    if (!customMealQuery.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/analyze-custom-meal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user_123',
          query: customMealQuery,
          goals: selectedGoals,
          age: userAge,
          recent_upgrades: recentUpgrades
        })
      });
      const data = await res.json();
      setSelectedItem({
        id: 'custom-' + Date.now(),
        name: data.food_name,
        calories: data.calories,
        protein: data.protein,
        sugar: data.sugar,
        fat: data.fat,
        carbs: data.carbs,
        initialData: data
      });
      setCustomMealQuery("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedGoals) {
    return <SaladBowlBuilder onSaveGoals={handleSaveGoals} />;
  }

  return (
    <div className="app-container">
      <header>
        <h1>Late Night Bites</h1>
        <p>Order your favorite food. We'll help you keep it smart.</p>
        <div className="header-actions">
          <div className="custom-meal-search">
            <input 
              type="text" 
              placeholder="Analyze any meal (e.g. Butter Chicken)"
              value={customMealQuery}
              onChange={(e) => setCustomMealQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAnalyzeCustomMeal()}
            />
            <button onClick={handleAnalyzeCustomMeal} disabled={loading}>
              {loading ? "..." : "Analyze"}
            </button>
          </div>
          <div className="active-goals-banner">
            <strong>Your Bowl:</strong> {userAge} <span style={{opacity: 0.4}}>|</span> {selectedGoals.join(" + ")}
            <button className="edit-goals-btn" onClick={() => setSelectedGoals(null)}>Edit Bowl</button>
          </div>
          <button 
            className="cravings-btn" 
            onClick={() => setShowCravings(true)}
          >
            🍫 Craving something specific?
          </button>
        </div>
      </header>

      <main>
        <FoodMenu onSelectItem={handleSelectItem} />
      </main>

      {selectedItem && (
        <CopilotModal 
          item={selectedItem} 
          goals={selectedGoals}
          age={userAge}
          recentUpgrades={recentUpgrades}
          onClose={handleCloseModal}
          onApplyUpgrade={handleApplyUpgrade}
          onUpgradeShown={handleUpgradeShown}
        />
      )}

      {showCravings && (
        <CravingsModal 
          age={userAge} 
          goals={selectedGoals} 
          onClose={() => setShowCravings(false)} 
        />
      )}
    </div>
  );
}

export default App;
