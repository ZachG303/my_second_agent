import React from 'react';
import ReportList from './components/ReportList';
import InflectionInsights from './components/InflectionInsights';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Earnings Agent AI</h1>
        <p>Agentic AI for earnings report analysis</p>
      </header>

      <main className="main-content">
        <ReportList />
        <div className="dashboard">
          <InflectionInsights />
        </div>
      </main>

      <footer className="app-footer">
        <p>Powered by LangChain &amp; LangGraph</p>
      </footer>
    </div>
  );
}

export default App;
