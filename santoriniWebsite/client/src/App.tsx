import { BrowserRouter, Route, Routes, Link} from "react-router-dom";
import GamePage from "./pages/game";
import IndexPage from "./pages/index";
import RulesPage from "./pages/rules";
import './App.css';

function App() {
  return (
      <BrowserRouter>
        <nav className="nav-bar">
          <Link to="/" className="nav-button">Home</Link>
          <Link to="/rules" className="nav-button">Rules</Link>
          <Link to="/game" className="nav-button">Play</Link>
        </nav>
        <Routes>
          <Route path="/" element={<IndexPage />}></Route>
          <Route path="/rules" element={<RulesPage />} /> 
          <Route path="/game" element={<GamePage />} />
        </Routes>
      </BrowserRouter>
  );
}

export default App;
