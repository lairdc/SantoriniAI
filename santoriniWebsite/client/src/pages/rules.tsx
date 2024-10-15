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
          <li>Move workers on the board.</li>
          <li>Construct buildings as you progress.</li>
          <li>Reach the top of a three-tiered building to win.</li>
        </ul>
      </div>
    </div>
  );
}
