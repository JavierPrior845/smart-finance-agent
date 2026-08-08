import { Plus } from 'lucide-react';
import './Pages.css';

export default function Accounts() {
  const accounts = [
    { id: 1, name: 'Main Checking', balance: 5450.00, type: 'BANK', isMain: true },
    { id: 2, name: 'Savings', balance: 7000.00, type: 'BANK', isMain: false },
  ];

  const investments = [
    { id: 1, ticker: 'AAPL', qty: 10, avgPrice: 150.0, currentPrice: 175.5, status: 'OPEN' },
    { id: 2, ticker: 'BTC', qty: 0.5, avgPrice: 40000.0, currentPrice: 38000.0, status: 'OPEN' },
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Cuentas & Inversiones</h1>
          <p className="page-subtitle">Gestión de liquidez y posiciones</p>
        </div>
        <button className="glass-button">
          <Plus size={18} />
          Nueva Cuenta
        </button>
      </div>

      <div className="accounts-grid">
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px' }}>Cuentas Bancarias</h3>
          <div className="account-list">
            {accounts.map(acc => (
              <div key={acc.id} className="account-card glass-panel">
                <div className="acc-info">
                  <h4>{acc.name} {acc.isMain && <span className="badge">Principal</span>}</h4>
                  <span className="acc-type">{acc.type}</span>
                </div>
                <div className="acc-balance">
                  €{acc.balance.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px' }}>Posiciones Abiertas</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Activo</th>
                <th>Cant.</th>
                <th>P&L</th>
              </tr>
            </thead>
            <tbody>
              {investments.map(inv => {
                const invested = inv.qty * inv.avgPrice;
                const current = inv.qty * inv.currentPrice;
                const pnl = current - invested;
                const isPositive = pnl >= 0;
                return (
                  <tr key={inv.id}>
                    <td><strong>{inv.ticker}</strong></td>
                    <td>{inv.qty}</td>
                    <td className={isPositive ? 'text-success' : 'text-danger'}>
                      {isPositive ? '+' : ''}€{pnl.toFixed(2)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
