import React, { useState } from 'react';

const GOAL_OPTIONS = [
  "Weight Loss",
  "Muscle Gain",
  "Weight Gain",
  "Low Sugar",
  "Balanced Diet",
  "High Protein",
  "High Fiber",
  "High Calcium",
  "High Iron",
  "Vitamin B12 Rich",
  "Low Carb",
  "Heart Healthy"
];

const AGE_OPTIONS = ["Teen", "Young Adult", "Adult", "Senior"];

export default function GoalSelector({ onSaveGoals }) {
  const [selected, setSelected] = useState([]);
  const [age, setAge] = useState("Young Adult");

  const toggleGoal = (goal) => {
    if (selected.includes(goal)) {
      setSelected(selected.filter(g => g !== goal));
    } else {
      setSelected([...selected, goal]);
    }
  };

  const handleSave = () => {
    const finalGoals = selected.length === 0 ? ["Balanced Diet"] : selected;
    onSaveGoals({ goals: finalGoals, age });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content goal-selector">
        <div className="modal-header">
          <h2>🎯 Set Your Profile</h2>
        </div>
        
        <div style={{ marginBottom: "2rem" }}>
          <h4 style={{ color: "var(--accent-color)", marginBottom: "0.5rem" }}>Your Age Group</h4>
          <div className="goals-grid">
            {AGE_OPTIONS.map(a => (
              <button 
                key={a}
                className={`goal-chip ${age === a ? 'active' : ''}`}
                onClick={() => setAge(a)}
              >
                {a}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <h4 style={{ color: "var(--accent-color)", marginBottom: "0.5rem" }}>Your Goals & Focus</h4>
          <p style={{ color: "var(--text-muted)", marginBottom: "1rem", fontSize: "0.9rem" }}>
            Select goals to personalize your SmartScore and AI suggestions.
          </p>
          <div className="goals-grid">
            {GOAL_OPTIONS.map(goal => (
              <button 
                key={goal}
                className={`goal-chip ${selected.includes(goal) ? 'active' : ''}`}
                onClick={() => toggleGoal(goal)}
              >
                {goal}
              </button>
            ))}
          </div>
        </div>

        <button className="btn-primary" style={{ width: '100%' }} onClick={handleSave}>
          Start Ordering
        </button>
      </div>
    </div>
  );
}
