import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import ElectricBorder from './components/ElectricBorder';
import ModelTester from './components/ModelTester';
import LegalTextGenerator from './components/LegalTextGenerator';

function App() {
  // Directly render the Legal Text Generator
  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#111827', 
      padding: '20px',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ 
          textAlign: 'center',
          marginBottom: '30px' 
        }}>
          <h1 style={{ 
            color: '#00ff7f', 
            fontSize: '3rem', 
            fontWeight: 'bold',
            margin: 0,
            marginBottom: '10px',
            textShadow: '0 0 12px rgba(0,255,127,0.35), 0 0 24px rgba(0,255,127,0.22)'
          }}>
            ⚖️ Thinkerbell Legal Text Generator
          </h1>
          <p style={{ 
            fontSize: '1.2rem', 
            color: '#94a3b8',
            margin: '0 auto',
            maxWidth: '800px'
          }}>
            Transform your rough ideas into professional legal templates. Enhanced model with <strong>96.4% accuracy</strong> and <strong>84.5% Recall@5</strong>.
          </p>
        </div>
        <LegalTextGenerator />
      </div>
    </div>
  );
}

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
}


