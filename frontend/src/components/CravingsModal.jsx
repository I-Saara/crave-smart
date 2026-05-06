import React, { useState } from 'react';

export default function CravingsModal({ age, goals, onClose }) {
  const [craving, setCraving] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!craving.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/craving-suggestions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ craving, age, goals })
      });
      if (!res.ok) throw new Error("API Error");
      const json = await res.json();
      setData(json);
    } catch (err) {
      // Offline fallback
      setTimeout(() => {
        setData({
          category: "sweet",
          alternatives: ["Dark chocolate", "Greek yogurt with cocoa powder", "Protein pudding"],
          reason: "These satisfy your sweet tooth while keeping protein high and sugar low."
        });
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🍫 Cravings Assistant</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {!data && !loading && (
          <form onSubmit={handleSubmit}>
            <p style={{ color: "var(--text-muted)", marginBottom: "1rem" }}>
              What are you craving right now? We'll find a smarter alternative based on your goals.
            </p>
            <input 
              type="text" 
              value={craving}
              onChange={e => setCraving(e.target.value)}
              placeholder="e.g. chocolate, chips, soda..."
              style={{
                width: '100%', padding: '1rem', borderRadius: '8px',
                border: '1px solid var(--accent-color)', background: 'rgba(255,255,255,0.05)',
                color: 'white', marginBottom: '1rem', fontSize: '1rem'
              }}
              autoFocus
            />
            <button type="submit" className="btn-primary" style={{ width: '100%' }}>Find Alternatives</button>
          </form>
        )}

        {loading && (
          <div className="loader-container">
            <div className="spinner"></div>
            <p>Finding smarter options...</p>
          </div>
        )}

        {data && (
          <div className="copilot-results">
            {data.category && (
               <div style={{ marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase' }}>
                 Category detected: <strong style={{ color: 'var(--accent-color)' }}>{data.category.replace('_', ' & ')}</strong>
               </div>
            )}
            <div className="insight-box" style={{ background: 'rgba(46, 213, 115, 0.1)', borderLeftColor: 'var(--success)' }}>
              <strong>Why these work:</strong> {data.reason}
            </div>
            
            <h4 style={{ color: 'var(--accent-color)', marginBottom: '1rem' }}>Smart Alternatives:</h4>
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {data.alternatives.map((alt, i) => (
                <li key={i} style={{ 
                  background: 'rgba(255,255,255,0.03)', padding: '1rem', 
                  borderRadius: '8px', marginBottom: '0.5rem', border: '1px solid rgba(255,255,255,0.05)'
                }}>✨ {alt}</li>
              ))}
            </ul>

            <button className="btn-secondary" style={{ width: '100%', marginTop: '1.5rem' }} onClick={onClose}>Close</button>
          </div>
        )}
      </div>
    </div>
  );
}
