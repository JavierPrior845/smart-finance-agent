import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Sidebar } from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Budgets from './pages/Budgets';
import Accounts from './pages/Accounts';
import Transactions from './pages/Transactions';
import ValidationInbox from './pages/ValidationInbox';
import Settings from './pages/Settings';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/budgets" element={<Budgets />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/inbox" element={<ValidationInbox />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
      <Toaster position="bottom-right" />
    </Router>
  );
}

export default App;
