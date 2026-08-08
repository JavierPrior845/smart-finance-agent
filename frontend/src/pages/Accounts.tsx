import { useState, useEffect } from 'react';
import { Plus, X, Loader2 } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Accounts() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    account_type: 'BANK',
    initial_balance: '0',
    currency: 'EUR',
    is_main: false
  });

  const fetchAccounts = async () => {
    try {
      setLoading(true);
      const res = await api.get('/accounts');
      setAccounts(res.data);
    } catch (error) {
      console.error("Error fetching accounts", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
  }, []);

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name) return;
    
    setSaving(true);
    try {
      await api.post('/accounts', {
        name: formData.name,
        account_type: formData.account_type,
        initial_balance: parseFloat(formData.initial_balance),
        currency: formData.currency,
        is_main: formData.is_main
      });
      setShowModal(false);
      setFormData({ name: '', account_type: 'BANK', initial_balance: '0', currency: 'EUR', is_main: false });
      await fetchAccounts();
    } catch (error) {
      console.error("Error creating account", error);
    } finally {
      setSaving(false);
    }
  };

  const investments = [
    { id: 1, ticker: 'AAPL', qty: 10, avgPrice: 150.0, currentPrice: 175.5, status: 'OPEN' },
    { id: 2, ticker: 'BTC', qty: 0.5, avgPrice: 40000.0, currentPrice: 38000.0, status: 'OPEN' },
  ];

  const totalLiquidity = accounts.reduce((sum, acc) => sum + acc.current_balance, 0);

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Cuentas & Inversiones</h1>
          <p className="page-subtitle">Liquidez Total: €{totalLiquidity.toFixed(2)}</p>
        </div>
        <button className="glass-button primary" onClick={() => setShowModal(true)}>
          <Plus size={18} />
          Nueva Cuenta
        </button>
      </div>

      <div className="accounts-grid">
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px' }}>Cuentas Bancarias y Billeteras</h3>
          <div className="account-list">
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                <Loader2 className="spin" size={32} />
              </div>
            ) : accounts.length === 0 ? (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No tienes cuentas registradas.</p>
            ) : (
              accounts.map(acc => (
                <div key={acc.id} className="account-card glass-panel">
                  <div className="acc-info">
                    <h4>{acc.name} {acc.is_main && <span className="badge">Principal</span>}</h4>
                    <span className="acc-type" style={{ opacity: 0.7 }}>{acc.account_type}</span>
                  </div>
                  <div className="acc-balance">
                    {acc.currency === 'EUR' ? '€' : acc.currency} {acc.current_balance.toFixed(2)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px' }}>Posiciones Abiertas</h3>
          <div className="table-responsive">
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

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px' }}>Posiciones Cerradas (Histórico)</h3>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Activo</th>
                  <th>Invertido</th>
                  <th>Retirado</th>
                  <th>P&L</th>
                  <th>ROI</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Módulo de inversiones próximamente...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modal Nueva Cuenta */}
      {showModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Nueva Cuenta</h3>
              <button onClick={() => setShowModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCreateAccount} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label>Nombre</label>
                <input 
                  type="text" 
                  required
                  value={formData.name} 
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  placeholder="Ej. Cuenta Nómina"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label>Tipo de Cuenta</label>
                <select 
                  value={formData.account_type} 
                  onChange={e => setFormData({...formData, account_type: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="BANK">Banco</option>
                  <option value="CASH">Efectivo</option>
                  <option value="WALLET">Billetera / Crypto</option>
                  <option value="CREDIT_CARD">Tarjeta de Crédito</option>
                </select>
              </div>

              <div className="input-group">
                <label>Saldo Inicial (€)</label>
                <input 
                  type="number" 
                  step="0.01"
                  required
                  value={formData.initial_balance} 
                  onChange={e => setFormData({...formData, initial_balance: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group" style={{ display: 'flex', alignItems: 'center', gap: '10px', flexDirection: 'row' }}>
                <input 
                  type="checkbox" 
                  id="is_main"
                  checked={formData.is_main} 
                  onChange={e => setFormData({...formData, is_main: e.target.checked})}
                  style={{ width: '18px', height: '18px' }}
                />
                <label htmlFor="is_main" style={{ margin: 0, cursor: 'pointer' }}>¿Es la cuenta principal?</label>
              </div>

              <button 
                type="submit" 
                className="glass-button primary" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}
                disabled={saving}
              >
                {saving ? <Loader2 className="spin" size={20} /> : 'Crear Cuenta'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
