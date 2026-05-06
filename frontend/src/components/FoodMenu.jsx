import React from 'react';
import { mockFoodItems } from '../data/mockFood';

export default function FoodMenu({ onSelectItem }) {
  return (
    <div className="menu-grid">
      {mockFoodItems.map(item => (
        <div key={item.id} className="food-card" onClick={() => onSelectItem(item)}>
          <div style={{ fontSize: '3rem', textAlign: 'center', marginBottom: '1rem' }}>
            {item.image}
          </div>
          <h3>{item.name}</h3>
          <div className="macros">
            <span>{item.calories} kcal</span>
            <span>{item.protein}g protein</span>
          </div>
          <button className="select-btn">Select Item</button>
        </div>
      ))}
    </div>
  );
}
