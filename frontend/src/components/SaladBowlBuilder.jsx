import React, { useState } from 'react';

const NUTRIENT_OPTIONS = [
  { id: "Protein", label: "Protein 🥩", color: "#ff7675" },
  { id: "Fiber", label: "Fiber 🥦", color: "#55efc4" },
  { id: "Calcium", label: "Calcium 🥛", color: "#74b9ff" },
  { id: "Iron", label: "Iron 🌿", color: "#00b894" },
  { id: "Vitamin B12 Rich", label: "B12 🍳", color: "#fdcb6e" },
  { id: "Low Sugar", label: "Low Sugar 🍬❌", color: "#fab1a0" },
  { id: "Low Carb", label: "Low Carb 🥖❌", color: "#ffeaa7" },
  { id: "Weight Loss", label: "Weight Loss ⚖️", color: "#81ecec" }
];

const AGE_OPTIONS = ["Teen", "Young Adult", "Adult", "Senior"];

export default function SaladBowlBuilder({ onSaveGoals }) {
  const [bowl, setBowl] = useState([]);
  const [age, setAge] = useState("Young Adult");

  const toggleIngredient = (nutrient) => {
    if (bowl.some(n => n.id === nutrient.id)) {
      setBowl(bowl.filter(n => n.id !== nutrient.id));
    } else {
      setBowl([...bowl, nutrient]);
    }
  };

  const handleSave = () => {
    const finalGoals = bowl.length === 0 ? ["Balanced Diet"] : bowl.map(n => n.id);
    onSaveGoals({ goals: finalGoals, age });
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content goal-selector" style={{ maxWidth: '600px' }}>
        <div className="modal-header">
          <h2>🥗 Build Your Nutrient Bowl</h2>
        </div>
        
        <div style={{ marginBottom: "1.5rem" }}>
          <h4 style={{ color: "var(--accent-color)", marginBottom: "0.5rem" }}>1. Select Your Age Group</h4>
          <div className="goals-grid">
            {AGE_OPTIONS.map(a => (
              <button 
                key={a}
                className={`goal-chip ${age === a ? 'active' : ''}`}
                onClick={() => setAge(a)}
                style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
              >
                {a}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <h4 style={{ color: "var(--accent-color)", marginBottom: "0.5rem" }}>2. Toss in Your Goals</h4>
          <p style={{ color: "var(--text-muted)", marginBottom: "1rem", fontSize: "0.9rem" }}>
            Click ingredients to add them to your personalized bowl.
          </p>
          <div className="goals-grid" style={{ gap: '0.5rem' }}>
            {NUTRIENT_OPTIONS.map(nutrient => {
              const inBowl = bowl.some(n => n.id === nutrient.id);
              return (
                <button 
                  key={nutrient.id}
                  className={`bowl-ingredient-btn ${inBowl ? 'added' : ''}`}
                  onClick={() => toggleIngredient(nutrient)}
                  style={{ borderColor: nutrient.color }}
                >
                  {nutrient.label} {inBowl && "✔️"}
                </button>
              );
            })}
          </div>
        </div>

        <div className="bowl-container">
          <div className="bowl-visual">
            {bowl.length === 0 ? (
              <div className="empty-bowl-text">Your bowl is empty! Add some nutrients.</div>
            ) : (
              <div className="bowl-contents">
                {bowl.map((n, idx) => (
                  <span key={idx} className="bowl-item" style={{ background: n.color }}>
                    {n.label}
                  </span>
                ))}
              </div>
            )}
          </div>
          <div className="bowl-base"></div>
        </div>

        <button className="btn-primary" style={{ width: '100%', marginTop: '2rem' }} onClick={handleSave}>
          Start Ordering
        </button>
      </div>
    </div>
  );
}
