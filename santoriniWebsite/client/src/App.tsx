import { BrowserRouter, Route, Routes, Link} from "react-router-dom";
import GamePage from "./pages/game";
import IndexPage from "./pages/index";
import RulesPage from "./pages/rules";
import './App.css';
import { useEffect } from "react";
import { useLocation } from "react-router-dom";

function ScrollToTop() {
    const { pathname } = useLocation();

    useEffect(() => {
        window.scrollTo(0, 0);
    }, [pathname]);

    return null;
}

function App() {
  return (
      <BrowserRouter>
      <ScrollToTop />
        <nav className="nav-bar">
          <Link to="/" className="nav-button">Home</Link>
          <Link to="/rules" className="nav-button">Rules</Link>
          <Link to="/game" className="nav-button">Play</Link>
        </nav>
        <div className="main-content">
          <Routes>
            <Route path="/" element={<IndexPage />}></Route>
            <Route path="/rules" element={<RulesPage />} /> 
            <Route path="/game" element={<GamePage />} />
          </Routes>
        </div>
      </BrowserRouter>
  );
}

export default App;
