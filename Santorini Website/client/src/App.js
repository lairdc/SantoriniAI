import React from 'react';
import './App.css'; 

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to SantoriniAI Board Game!</h1>
        <div>
          <button onClick={() => alert('Playing against a friend')}>
            Play Against a Friend
          </button>
          <button onClick={() => alert('Playing against AI')}>
            Play Against AI
          </button>
        </div>
      </header>
    </div>
  );
}

export default App;
