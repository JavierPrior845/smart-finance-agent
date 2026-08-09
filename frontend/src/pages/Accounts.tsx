import { useState, useEffect } from 'react';
import { Plus, X, Loader2 } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Accounts() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [investments, setInvestments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);

  const [showInvModal, setShowInvModal] = useState(false);
  const [savingInv, setSavingInv] = useState(false);

  const [showCloseInvModal, setShowCloseInvModal] = useState(false);
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);
  const [closeAmount, setCloseAmount] = useState('0');
  const [closingInv, setClosingInv] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    account_type: 'BANK',
    initial_balance: '0',
    currency: 'EUR',
    is_main: false
  });

  const [invFormData, setInvFormData] = useState({
    name: '',
    ticker: '',
    asset_type: 'STOCK',
    broker: '',
    invested_amount: '0',
    units_qty: '0',
    average_buy_price: '0'
  });

  const fetchAccountsAndInvestments = async () => {
    try {
      setLoading(true);
      const [accRes, invRes] = await Promise.all([
        api.get('/accounts'),
        api.get('/investments')
      ]);
      setAccounts(accRes.data);
      setInvestments(invRes.data);
    } catch (error) {
      console.error("Error fetching data", error);
    } finally {
      setLoading(false);
    }
  };

  const syncInvestments = async () => {
    try {
      await api.post('/investments/sync');
      // Later this will refetch investment list
    } catch (error) {
      console.error("Error syncing investments", error);
    }
  };

  useEffect(() => {
    fetchAccountsAndInvestments();
    syncInvestments(); // Silent sync in background
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
      await fetchAccountsAndInvestments();
    } catch (error) {
      console.error("Error creating account", error);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateInvestment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!invFormData.name || !invFormData.ticker || !invFormData.broker) return;
    
    setSavingInv(true);
    try {
      await api.post('/investments', {
        name: invFormData.name,
        ticker: invFormData.ticker,
        asset_type: invFormData.asset_type,
        broker: invFormData.broker,
        invested_amount: parseFloat(invFormData.invested_amount),
        units_qty: parseFloat(invFormData.units_qty) || null,
        average_buy_price: parseFloat(invFormData.average_buy_price) || null,
      });
      setShowInvModal(false);
      setInvFormData({ name: '', ticker: '', asset_type: 'STOCK', broker: '', invested_amount: '0', units_qty: '0', average_buy_price: '0' });
      await fetchAccountsAndInvestments();
      await syncInvestments(); // Sync the new ticker
    } catch (error) {
      console.error("Error creating investment", error);
    } finally {
      setSavingInv(false);
    }
  };

  const handleCloseInvestment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssetId) return;

    setClosingInv(true);
    try {
      await api.post(`/investments/${selectedAssetId}/close`, {
        withdrawn_amount: parseFloat(closeAmount)
      });
      setShowCloseInvModal(false);
      setSelectedAssetId(null);
      setCloseAmount('0');
      await fetchAccountsAndInvestments();
    } catch (error) {
      console.error("Error closing investment", error);
    } finally {
      setClosingInv(false);
    }
  };

  const totalLiquidity = accounts.reduce((sum, acc) => sum + acc.current_balance, 0);
  const openPositions = investments.filter(inv => inv.status === 'OPEN');
  const closedPositions = investments.filter(inv => inv.status === 'CLOSED');

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Cuentas & Inversiones</h1>
          <p className="page-subtitle">Liquidez Total: €{totalLiquidity.toFixed(2)}</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="glass-button primary" onClick={() => setShowModal(true)}>
            <Plus size={18} />
            Nueva Cuenta
          </button>
          <button className="glass-button success" onClick={() => setShowInvModal(true)}>
            <Plus size={18} />
            Nueva Inversión
          </button>
        </div>
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
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {openPositions.length === 0 && <tr><td colSpan={4} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No tienes posiciones abiertas</td></tr>}
                {openPositions.map(inv => {
                  const invested = inv.invested_amount;
                  const current = inv.total_value !== null ? inv.total_value : invested; // Fallback if no snapshot yet
                  const pnl = current - invested;
                  const isPositive = pnl >= 0;
                  return (
                    <tr key={inv.id}>
                      <td><strong>{inv.ticker || inv.name}</strong></td>
                      <td>{inv.units_qty || '-'}</td>
                      <td className={isPositive ? 'text-success' : 'text-danger'}>
                        {isPositive ? '+' : ''}€{pnl.toFixed(2)}
                      </td>
                      <td>
                        <button 
                          className="glass-button" 
                          style={{ padding: '4px 8px', fontSize: '12px', background: 'rgba(255, 71, 87, 0.2)', color: '#ff4757', borderColor: 'rgba(255, 71, 87, 0.4)' }}
                          onClick={() => { setSelectedAssetId(inv.id); setShowCloseInvModal(true); }}
                        >
                          Cerrar
                        </button>
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
                {closedPositions.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No tienes posiciones cerradas</td></tr>}
                {closedPositions.map(inv => {
                  const invested = inv.invested_amount;
                  const withdrawn = inv.withdrawn_amount;
                  const pnl = inv.realized_pnl;
                  const isPositive = pnl >= 0;
                  const roi = invested > 0 ? (pnl / invested) * 100 : 0;
                  
                  return (
                    <tr key={inv.id}>
                      <td><strong>{inv.ticker || inv.name}</strong></td>
                      <td>€{invested.toFixed(2)}</td>
                      <td>€{withdrawn.toFixed(2)}</td>
                      <td className={isPositive ? 'text-success' : 'text-danger'}>
                        {isPositive ? '+' : ''}€{pnl.toFixed(2)}
                      </td>
                      <td className={isPositive ? 'text-success' : 'text-danger'}>
                        {isPositive ? '+' : ''}{roi.toFixed(1)}%
                      </td>
                    </tr>
                  );
                })}
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

      {/* Modal Nueva Inversión */}
      {showInvModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '450px', padding: '24px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Nueva Inversión</h3>
              <button onClick={() => setShowInvModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCreateInvestment} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', gap: '16px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Nombre</label>
                  <input 
                    type="text" 
                    required
                    value={invFormData.name} 
                    onChange={e => setInvFormData({...invFormData, name: e.target.value})}
                    placeholder="Ej. Mis Bitcoins"
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Ticker (Yahoo Finance)</label>
                  <input 
                    type="text" 
                    required
                    value={invFormData.ticker} 
                    onChange={e => setInvFormData({...invFormData, ticker: e.target.value.toUpperCase()})}
                    placeholder="Ej. BTC-USD, AAPL"
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', gap: '16px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Tipo de Activo</label>
                  <select 
                    value={invFormData.asset_type} 
                    onChange={e => setInvFormData({...invFormData, asset_type: e.target.value})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  >
                    <option value="STOCK">Acción</option>
                    <option value="ETF">ETF / Fondo</option>
                    <option value="CRYPTO">Criptomoneda</option>
                    <option value="BOND">Bono</option>
                  </select>
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Broker / Plataforma</label>
                  <input 
                    type="text" 
                    required
                    value={invFormData.broker} 
                    onChange={e => setInvFormData({...invFormData, broker: e.target.value})}
                    placeholder="Ej. Binance, MyInvestor"
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Total Invertido (€)</label>
                <input 
                  type="number" 
                  step="0.01"
                  required
                  value={invFormData.invested_amount} 
                  onChange={e => setInvFormData({...invFormData, invested_amount: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '16px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Unidades Compradas</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    value={invFormData.units_qty} 
                    onChange={e => setInvFormData({...invFormData, units_qty: e.target.value})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Precio Medio de Compra</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    value={invFormData.average_buy_price} 
                    onChange={e => setInvFormData({...invFormData, average_buy_price: e.target.value})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <button 
                type="submit" 
                className="glass-button success" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}
                disabled={savingInv}
              >
                {savingInv ? <Loader2 className="spin" size={20} /> : 'Registrar Inversión'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Cerrar Inversión */}
      {showCloseInvModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, color: '#ff4757' }}>Cerrar Inversión</h3>
              <button onClick={() => { setShowCloseInvModal(false); setSelectedAssetId(null); }} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCloseInvestment} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginBottom: '8px' }}>
                Indica la cantidad final exacta que has recibido al vender o retirar esta inversión.
              </p>
              
              <div className="input-group">
                <label>Cantidad Recibida (€)</label>
                <input 
                  type="number" 
                  step="0.01"
                  required
                  value={closeAmount} 
                  onChange={e => setCloseAmount(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <button 
                type="submit" 
                className="glass-button" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center', background: '#ff4757', color: '#fff', border: 'none' }}
                disabled={closingInv}
              >
                {closingInv ? <Loader2 className="spin" size={20} /> : 'Confirmar Venta'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
