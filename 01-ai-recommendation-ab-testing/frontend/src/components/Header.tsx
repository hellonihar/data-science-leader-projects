import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="app-header">
      <div className="header-content">
        <h1>
          <Link to="/">AI Recommendation A/B Testing</Link>
        </h1>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/experiments">Experiments</Link>
          <Link to="/recommendations">Recommendations</Link>
        </nav>
      </div>
    </header>
  );
}
