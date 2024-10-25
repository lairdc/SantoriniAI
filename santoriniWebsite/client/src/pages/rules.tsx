import '../fonts.css';
import './rules.css';

export default function RulesPage() {
  return (
    <div className="rules-app">
      <header className="rules-app-header">
        <h1>Game Rules</h1>
      </header>
      <div className="rules-content">
        <ul>
          <li>The goal of Santorini is to be the first player to move one of your workers to the third level of any building.</li>
          <br />
          <br />
          
          <li><strong>Components: </strong></li>
          <li> - 22 Level 1 Blocks (bottom level)</li>
          <li> - 18 Level 2 Blocks (middle level)</li>
          <li> - 14 Level 3 blocks (top level)</li>
          <li> - 18 Domes (used to cap towers)</li>
          <li> - 6 Worker pieces (3 of each color for two players)</li>
          <br />
          <br />

          <li><strong>Setup: </strong></li>
          <li> 1. Place the game board in the center of the play area.</li>
          <li> 2. Each player chooses a color and takes two workers of that color.</li>
          <li> 3. Players decide who goes first. The first player places one of their workers on any unoccupied space of the 5x5 grid, followed by the second player placing one of their workers. Continue alternating placements until both players have placed their two workers.</li>
          <br />
          <br />

          <li><strong>Gameplay: </strong></li>
          <li>Players take turns performing the following steps in order:</li>
          <li> - <strong>Move:</strong> Choose one of your workers and move it to an adjacent space (horizontally, vertically, or diagonally). You may move up only one level, but you can move down any number of levels.</li>
          <li> - <strong>Build:</strong> After moving, the worker that moved must build a block on an adjacent space (horizontally, vertically, or diagonally). Build one level higher or place a dome on a third-level building to cap it.</li>
          <br />
          <br />

          <li><strong>Winning the Game: </strong></li>
          <li> The game is won when a player moves one of their workers onto the third level of a building.</li>
          <br />
          <br />

          <li><strong>Additional Rules: </strong></li>
          <li> - <strong>Blocking with Domes:</strong> Players can place domes on third-level buildings to prevent opponents from moving onto that space.</li>
          <li> - <strong>Moving Down:</strong> Workers can move down any number of levels in one move, which can be useful for positioning.</li>
          <li> - <strong>Edge of the Board:</strong> Workers can move to and build at the edge of the 5x5 grid just like any other space.</li>
          <li> - <strong>Endgame Blockage:</strong> If both players reach a point where neither can win due to blocked spaces or capped domes, the game ends in a draw.</li>
        </ul>
      </div>
    </div>
  );
}