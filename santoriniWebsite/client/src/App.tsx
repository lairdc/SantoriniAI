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

      <div className="game-overview">
        <div className="game-overview-left">
          <div>
          <h2><b>Game Overview</b></h2>
          <p>Santorini is a strategic board game where players to move their workers and construct buildings across the evolving board. 
            The goal is to maneuver your workers to the top of a three-tiered structure. Players can also harness the power of Greek gods, 
            adding unique abilities that influence the flow of the game.
          </p>
          </div>
          
          <div className="button-container">
            <button onClick={() => alert('Playing against a friend')}>
              Play Against Friend
            </button>
            <button onClick={() => alert('Playing against AI')}>
              Play Against AI
            </button>
          </div>
        </div>
        <div className="game-overview-img">
          <img src="/clouds.png" alt="Santorini Game" />
        </div>
      </div>
    </div>
  );
}

export default App;
