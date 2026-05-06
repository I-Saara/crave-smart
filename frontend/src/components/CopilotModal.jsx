import React, { useState, useEffect } from 'react';

export default function CopilotModal({ item, goals, age, recentUpgrades, onClose, onApplyUpgrade, onUpgradeShown }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    // Simulate API call to FastAPI backend
    // Since we want the demo to work without needing the backend running immediately,
    // we'll try to hit the backend, but fallback to mocked data if it fails.
    const fetchScore = async () => {
      if (item.initialData) {
        setData(item.initialData);
        onUpgradeShown(item.initialData.upgrade);
        setLoading(false);
        return;
      }
      try {
        const res = await fetch('http://localhost:8000/score-meal', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 'user_123',
            food_name: item.name,
            calories: item.calories,
            protein: item.protein,
            sugar: item.sugar || 0,
            fat: item.fat || 0,
            fiber: item.fiber || 0,
            calcium: item.calcium || 0,
            iron: item.iron || 0,
            b12: item.b12 || 0,
            carbs: item.carbs || 0,
            order_time_iso: new Date().toISOString(),
            goals: goals,
            age: age,
            recent_upgrades: recentUpgrades
          })
        });
        
        if (!res.ok) throw new Error('API Error');
        const json = await res.json();
        setData(json);
        onUpgradeShown(json.upgrade);
      } catch (err) {
        // Fallback for UI Demo purposes with heuristic rules
        setTimeout(() => {
          let fallbackScore = item.calories > 600 ? 45 : 85;
          let fallbackUpgrade = "Add a side of veggies.";
          let fallbackAlt = "Grilled Chicken Salad";
          const category = item.name.toLowerCase();
          if (category.includes("burger")) fallbackAlt = "A grilled chicken wrap or bunless patty.";
          else if (category.includes("pizza")) fallbackAlt = "A thin-crust veggie pizza or salad.";
          else if (category.includes("shake") || category.includes("soda")) fallbackAlt = "Sparkling water or green tea.";
          else if (category.includes("nachos") || category.includes("fries")) fallbackAlt = "Baked sweet potato wedges.";

          if (goals.includes("Muscle Gain") && item.protein < 20) {
            fallbackUpgrade = "Add grilled chicken or double the protein portion.";
          } else if (goals.includes("Low Sugar") && item.sugar > 10) {
            fallbackUpgrade = "Swap soda for a zero-sugar alternative.";
          } else if (item.calories > 800) {
            fallbackUpgrade = "Choose a smaller portion or remove extra cheese.";
          }

          if (goals.includes("Weight Gain")) {
            fallbackScore += 20; // boost score for dense foods
          }

          setData({
            smart_score: Math.min(100, fallbackScore),
            score_breakdown: { base: fallbackScore, nutrient_boost: 0 },
            insight: item.calories > 600 
              ? `This ${item.name} is heavier than your usual late-night choices.`
              : `Great! This ${item.name} is a light and smart choice.`,
            explanation: `Tailored analysis for ${item.name} based on your goals.`,
            alternative: fallbackAlt,
            upgrade: fallbackUpgrade,
            nutrient_gain: {
              "fiber": { "change_text": "+5g fiber", "new_total": `${(item.fiber || 0) + 5}g` },
              "calories": { "change_text": "+45kcal calories", "new_total": `${(item.calories || 0) + 45}kcal` }
            }
          });
          onUpgradeShown(fallbackUpgrade);
        }, 1500);
      } finally {
        setLoading(false);
      }
    };

    fetchScore();
  }, [item]);

  if (!item) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Nutrition Copilot</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {loading ? (
          <div className="loader-container">
            <div className="spinner"></div>
            <p>Analyzing your choice...</p>
          </div>
        ) : (
          <div className="copilot-results">
            <div className={`score-circle ${data.smart_score >= 70 ? 'high' : data.smart_score >= 50 ? 'medium' : 'low'}`}>
              <div className="score-value">{data.smart_score}</div>
              <div className="score-label">SmartScore</div>
            </div>

            <div className="insight-box">
              <strong>Behavior Insight:</strong> {data.insight}
            </div>

            <div className="ai-suggestion">
              <h4>Explanation</h4>
              <p>{data.explanation}</p>
            </div>

            <div className="ai-suggestion">
              <h4>Alternative</h4>
              <p>{data.alternative}</p>
            </div>

            <div className="ai-suggestion">
              <h4>Simple Upgrade</h4>
              <p>
                {data.upgrade}
                {data.nutrient_gain && Object.entries(data.nutrient_gain).map(([key, val]) => (
                  <span key={key} className="nutrient-badge">[{val.change_text} → Total: {val.new_total}]</span>
                ))}
              </p>
            </div>

            <div className="action-buttons">
              <button className="btn-secondary" onClick={onClose}>Ignore</button>
              <button className="btn-primary" onClick={() => onApplyUpgrade(data.upgrade)}>Apply Upgrade</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
