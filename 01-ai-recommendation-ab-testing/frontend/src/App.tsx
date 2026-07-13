import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Dashboard from "./pages/Dashboard";
import Experiments from "./pages/Experiments";
import Recommendations from "./pages/Recommendations";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/experiments" element={<Experiments />} />
          <Route path="/recommendations" element={<Recommendations />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;
