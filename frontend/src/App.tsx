import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Sidebar } from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Budgets from './pages/Budgets';
import Accounts from './pages/Accounts';
import Transactions from './pages/Transactions';
import ValidationInbox from './pages/ValidationInbox';
import Settings from './pages/Settings';
import Login from './pages/Login';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Loader2 } from 'lucide-react';
import './App.css';

function MainApp() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: 'var(--bg-app)',
          color: 'var(--text-secondary)',
          gap: '1rem',
        }}
      >
        <Loader2 size={32} className="animate-spin" style={{ color: 'var(--color-primary-light)' }} />
        <span style={{ fontSize: '0.9rem' }}>Cargando sesión segura...</span>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  return (
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
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <MainApp />
        <Toaster position="bottom-right" />
      </AuthProvider>
    </Router>
  );
}

export default App;
