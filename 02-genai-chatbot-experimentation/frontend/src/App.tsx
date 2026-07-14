import { Routes, Route, NavLink } from 'react-router-dom';
import ChatPage from './pages/ChatPage';
import ExperimentsPage from './pages/ExperimentsPage';
import DashboardPage from './pages/DashboardPage';
import GovernancePage from './pages/GovernancePage';
import DocumentsPage from './pages/DocumentsPage';
import SettingsPage from './pages/SettingsPage';

function Nav() {
  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `px-3 py-2 rounded-md text-sm font-medium transition-colors ${
      isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-700 hover:text-white'
    }`;

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-1">
            <span className="text-white font-bold text-lg mr-4">GenAI Chatbot Hub</span>
            <NavLink to="/" end className={linkClass}>Chat</NavLink>
            <NavLink to="/experiments" className={linkClass}>Experiments</NavLink>
            <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
            <NavLink to="/governance" className={linkClass}>Governance</NavLink>
            <NavLink to="/documents" className={linkClass}>Documents</NavLink>
            <NavLink to="/settings" className={linkClass}>Settings</NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <Nav />
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/experiments" element={<ExperimentsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/governance" element={<GovernancePage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </main>
    </div>
  );
}
