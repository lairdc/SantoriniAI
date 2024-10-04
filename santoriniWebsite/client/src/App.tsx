import React from 'react';
import './fonts.css';
import './App.css'; 

function App() {
  return (
    <div className="App">
      <header className="App-header">
      <h1>
        <span className="welcome">Welcome to </span>
        <span className="santorini">SantoriniAI</span>
        <span className="welcome"> Board Game!</span>
      </h1>
      </header>
        <div className="button-container">
          <button onClick={() => alert('Playing against a friend')}>
            Play Against Friend
          </button>
          <button onClick={() => alert('Playing against AI')}>
            Play Against AI
          </button>
        </div>
    </div>
  );
}

export default App;
