import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Wallet, PiggyBank, History, Inbox, Settings } from 'lucide-react';
import clsx from 'clsx';
import './Sidebar.css';

export function Sidebar() {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/budgets', icon: PiggyBank, label: 'Presupuestos' },
    { to: '/accounts', icon: Wallet, label: 'Cuentas' },
    { to: '/transactions', icon: History, label: 'Histórico' },
    { to: '/inbox', icon: Inbox, label: 'Inbox' },
  ];

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <div className="logo-glow"></div>
        <h2>Smart Finance</h2>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => clsx('nav-item', isActive && 'active')}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <NavLink to="/settings" className={({ isActive }) => clsx('nav-item', isActive && 'active')}>
          <Settings size={20} />
          <span>Configuración</span>
        </NavLink>
      </div>
    </aside>
  );
}
