import { useState, useEffect } from 'react';
import { Plus, Minus, X, Loader2, History, TrendingUp, TrendingDown } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

interface InvestmentMovement {
  id: string;
  asset_id: string;
  movement_type: string;
  amount: number;
  units?: number;
  unit_price?: number;
  movement_date: string;
  notes?: string;
}

export default function Accounts() {
  const [accounts, setAccounts] = useState<any[]>([]);
  const [investments, setInvestments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Modales Cuentas & Nueva Inversión
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showInvModal, setShowInvModal] = useState(false);
  const [savingInv, setSavingInv] = useState(false);

  // Modales Avanzados de Inversiones (DCA, Venta Parcial, Historial)
  const [selectedAsset, setSelectedAsset] = useState<any | null>(null);
  
  // Modal Comprar Más (DCA)
  const [showBuyMoreModal, setShowBuyMoreModal] = useState(false);
  const [buyMoreData, setBuyMoreData] = useState({ units: '', unit_price: '', notes: '', source_account_id: '' });
  const [savingBuyMore, setSavingBuyMore] = useState(false);

  // Modal Vender (Parcial o Total)
  const [showSellModal, setShowSellModal] = useState(false);
  const [sellData, setSellData] = useState({ units: '', unit_price: '', notes: '', destination_account_id: '' });
  const [savingSell, setSavingSell] = useState(false);

  // Modal Historial Movimientos
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [assetMovements, setAssetMovements] = useState<InvestmentMovement[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

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
    average_buy_price: '0',
    source_account_id: ''
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
    } catch (error) {
      console.error("Error syncing investments", error);
    }
  };

  useEffect(() => {
    fetchAccountsAndInvestments();
    syncInvestments();
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
        units_qty: invFormData.units_qty ? parseFloat(invFormData.units_qty) : null,
        average_buy_price: invFormData.average_buy_price ? parseFloat(invFormData.average_buy_price) : null,
        source_account_id: invFormData.source_account_id || null
      });
      setShowInvModal(false);
      setInvFormData({ name: '', ticker: '', asset_type: 'STOCK', broker: '', invested_amount: '0', units_qty: '0', average_buy_price: '0', source_account_id: '' });
      await fetchAccountsAndInvestments();
      await syncInvestments();
    } catch (error) {
      console.error("Error creating investment", error);
    } finally {
      setSavingInv(false);
    }
  };

  // 1. Ejecutar Comprar Más (DCA)
  const handleBuyMore = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAsset || !buyMoreData.units || !buyMoreData.unit_price) return;

    setSavingBuyMore(true);
    try {
      await api.post(`/investments/${selectedAsset.id}/buy`, {
        units: parseFloat(buyMoreData.units),
        unit_price: parseFloat(buyMoreData.unit_price),
        notes: buyMoreData.notes || null,
        source_account_id: buyMoreData.source_account_id || null
      });
      setShowBuyMoreModal(false);
      setSelectedAsset(null);
      setBuyMoreData({ units: '', unit_price: '', notes: '', source_account_id: '' });
      await fetchAccountsAndInvestments();
    } catch (error) {
      console.error("Error buying more investment units", error);
    } finally {
      setSavingBuyMore(false);
    }
  };

  // 2. Ejecutar Vender Unidades (Parcial/Total)
  const handleSellUnits = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAsset || !sellData.units || !sellData.unit_price) return;

    setSavingSell(true);
    try {
      await api.post(`/investments/${selectedAsset.id}/sell`, {
        units: parseFloat(sellData.units),
        unit_price: parseFloat(sellData.unit_price),
        notes: sellData.notes || null,
        destination_account_id: sellData.destination_account_id || null
      });
      setShowSellModal(false);
      setSelectedAsset(null);
      setSellData({ units: '', unit_price: '', notes: '', destination_account_id: '' });
      await fetchAccountsAndInvestments();
    } catch (error) {
      console.error("Error selling investment units", error);
    } finally {
      setSavingSell(false);
    }
  };

  // 3. Cargar Historial de Movimientos
  const handleOpenHistory = async (asset: any) => {
    setSelectedAsset(asset);
    setShowHistoryModal(true);
    setLoadingHistory(true);
    try {
      const res = await api.get(`/investments/${asset.id}/movements`);
      setAssetMovements(res.data);
    } catch (error) {
      console.error("Error fetching investment movements", error);
    } finally {
      setLoadingHistory(false);
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
          <p className="page-subtitle">Liquidez Bancaria Total: €{totalLiquidity.toFixed(2)}</p>
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
        {/* Panel Cuentas */}
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

        {/* Panel Posiciones Abiertas */}
        <div className="glass-panel" style={{ padding: '24px', gridColumn: 'span 2' }}>
          <h3 style={{ marginBottom: '24px' }}>Posiciones Abiertas en Cartera</h3>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Activo</th>
                  <th>Broker</th>
                  <th>Unidades</th>
                  <th>PMP (€)</th>
                  <th>Invertido Actual</th>
                  <th>P&L Realizado</th>
                  <th>P&L Latente</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {openPositions.length === 0 && (
                  <tr><td colSpan={8} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No tienes posiciones abiertas</td></tr>
                )}
                {openPositions.map(inv => {
                  const invested = inv.invested_amount;
                  const currentVal = inv.total_value !== null && inv.total_value !== undefined ? inv.total_value : invested;
                  const unrealizedPnl = currentVal - invested;
                  const isUnrealizedPos = unrealizedPnl >= 0;
                  const isRealizedPos = inv.realized_pnl >= 0;
                  const pmp = inv.average_buy_price || (inv.units_qty ? invested / inv.units_qty : 0);

                  return (
                    <tr key={inv.id}>
                      <td>
                        <strong>{inv.ticker || inv.name}</strong>
                        <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{inv.name}</span>
                      </td>
                      <td><span className="badge" style={{ background: 'rgba(255,255,255,0.08)' }}>{inv.broker}</span></td>
                      <td>{inv.units_qty !== null ? inv.units_qty.toFixed(4) : '-'}</td>
                      <td>€{pmp.toFixed(2)}</td>
                      <td>€{invested.toFixed(2)}</td>
                      <td style={{ color: isRealizedPos ? 'var(--color-success)' : 'var(--color-danger)', fontWeight: 600 }}>
                        {isRealizedPos ? '+' : ''}€{inv.realized_pnl.toFixed(2)}
                      </td>
                      <td style={{ color: isUnrealizedPos ? 'var(--color-success)' : 'var(--color-danger)', fontWeight: 600 }}>
                        {isUnrealizedPos ? '+' : ''}€{unrealizedPnl.toFixed(2)}
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'flex-end' }}>
                          <button 
                            className="glass-button" 
                            style={{ padding: '4px 8px', fontSize: '12px', background: 'rgba(0, 255, 127, 0.15)', color: 'var(--color-success)', borderColor: 'rgba(0, 255, 127, 0.3)' }}
                            onClick={() => { setSelectedAsset(inv); setShowBuyMoreModal(true); }}
                            title="Comprar más unidades (DCA)"
                          >
                            <Plus size={14} /> Comprar
                          </button>
                          <button 
                            className="glass-button" 
                            style={{ padding: '4px 8px', fontSize: '12px', background: 'rgba(255, 51, 102, 0.15)', color: 'var(--color-danger)', borderColor: 'rgba(255, 51, 102, 0.3)' }}
                            onClick={() => { 
                              setSelectedAsset(inv); 
                              setSellData({ units: inv.units_qty ? inv.units_qty.toString() : '', unit_price: pmp.toString(), notes: '', destination_account_id: '' });
                              setShowSellModal(true); 
                            }}
                            title="Vender parcial o totalmente"
                          >
                            <Minus size={14} /> Vender
                          </button>
                          <button 
                            className="glass-button" 
                            style={{ padding: '4px 8px', fontSize: '12px' }}
                            onClick={() => handleOpenHistory(inv)}
                            title="Ver historial de operaciones"
                          >
                            <History size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Panel Posiciones Cerradas */}
        <div className="glass-panel" style={{ padding: '24px', gridColumn: 'span 2' }}>
          <h3 style={{ marginBottom: '24px' }}>Posiciones Cerradas (Histórico)</h3>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Activo</th>
                  <th>Broker</th>
                  <th>Total Retirado (€)</th>
                  <th>Ganancia Realizada (€)</th>
                  <th>Historial</th>
                </tr>
              </thead>
              <tbody>
                {closedPositions.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No tienes posiciones cerradas</td></tr>}
                {closedPositions.map(inv => {
                  const withdrawn = inv.withdrawn_amount;
                  const pnl = inv.realized_pnl;
                  const isPositive = pnl >= 0;
                  
                  return (
                    <tr key={inv.id}>
                      <td><strong>{inv.ticker || inv.name}</strong></td>
                      <td>{inv.broker}</td>
                      <td>€{withdrawn.toFixed(2)}</td>
                      <td style={{ color: isPositive ? 'var(--color-success)' : 'var(--color-danger)', fontWeight: 600 }}>
                        {isPositive ? '+' : ''}€{pnl.toFixed(2)}
                      </td>
                      <td>
                        <button 
                          className="glass-button" 
                          style={{ padding: '4px 8px', fontSize: '12px' }}
                          onClick={() => handleOpenHistory(inv)}
                        >
                          <History size={14} /> Ver
                        </button>
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
          <div className="glass-panel" style={{ width: '480px', padding: '24px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Nueva Posición de Inversión</h3>
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
                    placeholder="Ej. Binance, Trade Republic"
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Total Invertido Inicialmente (€)</label>
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
                  <label>Precio Unitario (€)</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    value={invFormData.average_buy_price} 
                    onChange={e => setInvFormData({...invFormData, average_buy_price: e.target.value})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Cuenta Origen de Pago (Opcional)</label>
                <select 
                  value={invFormData.source_account_id} 
                  onChange={e => setInvFormData({...invFormData, source_account_id: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">Selecciona cuenta...</option>
                  {accounts.map(acc => (
                    <option key={acc.id} value={acc.id}>{acc.name} (€{acc.current_balance.toFixed(2)})</option>
                  ))}
                </select>
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

      {/* Modal Comprar Más (DCA) */}
      {showBuyMoreModal && selectedAsset && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.75)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(6px)'
        }}>
          <div className="glass-panel" style={{ width: '420px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, color: 'var(--color-success)' }}>
                Comprar más de {selectedAsset.ticker || selectedAsset.name} (DCA)
              </h3>
              <button onClick={() => { setShowBuyMoreModal(false); setSelectedAsset(null); }} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
              El Precio Medio Ponderado (PMP) y las unidades totales se recalcularán automáticamente.
            </p>

            <form onSubmit={handleBuyMore} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', gap: '12px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Nuevas Unidades</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    required
                    value={buyMoreData.units}
                    onChange={e => setBuyMoreData({...buyMoreData, units: e.target.value})}
                    placeholder="Ej. 0.5"
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Precio por Unidad (€)</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    required
                    value={buyMoreData.unit_price}
                    onChange={e => setBuyMoreData({...buyMoreData, unit_price: e.target.value})}
                    placeholder="Ej. 250.0"
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Cuenta de Pago (Opcional)</label>
                <select 
                  value={buyMoreData.source_account_id} 
                  onChange={e => setBuyMoreData({...buyMoreData, source_account_id: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">Selecciona cuenta...</option>
                  {accounts.map(acc => (
                    <option key={acc.id} value={acc.id}>{acc.name} (€{acc.current_balance.toFixed(2)})</option>
                  ))}
                </select>
              </div>

              <button 
                type="submit" 
                className="glass-button success" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}
                disabled={savingBuyMore}
              >
                {savingBuyMore ? <Loader2 className="spin" size={20} /> : 'Confirmar Compra DCA'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Vender Unidades (Parcial/Total) */}
      {showSellModal && selectedAsset && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.75)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(6px)'
        }}>
          <div className="glass-panel" style={{ width: '420px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0, color: 'var(--color-danger)' }}>
                Vender {selectedAsset.ticker || selectedAsset.name}
              </h3>
              <button onClick={() => { setShowSellModal(false); setSelectedAsset(null); }} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Unidades actuales disponibles: <strong>{selectedAsset.units_qty}</strong>. Si vendes todas las unidades, la posición se cerrará.
            </p>

            <form onSubmit={handleSellUnits} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', gap: '12px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Unidades a Vender</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    required
                    value={sellData.units}
                    onChange={e => setSellData({...sellData, units: e.target.value})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label>Precio Venta (€/u)</label>
                  <input 
                    type="number" 
                    step="0.00000001"
                    required
                    value={sellData.unit_price}
                    onChange={e => setSellData({...sellData, unit_price: e.target.value})}
                    style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Cuenta Destino del Dinero (Opcional)</label>
                <select 
                  value={sellData.destination_account_id} 
                  onChange={e => setSellData({...sellData, destination_account_id: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">Selecciona cuenta...</option>
                  {accounts.map(acc => (
                    <option key={acc.id} value={acc.id}>{acc.name} (€{acc.current_balance.toFixed(2)})</option>
                  ))}
                </select>
              </div>

              <button 
                type="submit" 
                className="glass-button" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center', background: 'var(--color-danger)', color: '#fff', border: 'none' }}
                disabled={savingSell}
              >
                {savingSell ? <Loader2 className="spin" size={20} /> : 'Confirmar Venta'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Historial de Movimientos */}
      {showHistoryModal && selectedAsset && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.8)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(6px)'
        }}>
          <div className="glass-panel" style={{ width: '560px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3 style={{ margin: 0 }}>Historial: {selectedAsset.ticker || selectedAsset.name}</h3>
              <button onClick={() => { setShowHistoryModal(false); setSelectedAsset(null); }} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <div style={{ overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {loadingHistory ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                  <Loader2 className="spin" size={28} />
                </div>
              ) : assetMovements.length === 0 ? (
                <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Sin historial registrado.</p>
              ) : (
                assetMovements.map(m => {
                  const isBuy = m.movement_type === 'BUY_MORE';
                  const dateStr = new Date(m.movement_date).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' });

                  return (
                    <div key={m.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {isBuy ? <TrendingUp size={18} style={{ color: 'var(--color-success)' }} /> : <TrendingDown size={18} style={{ color: 'var(--color-danger)' }} />}
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{isBuy ? 'Compra (DCA)' : 'Venta'} {m.units ? `(${m.units} u)` : ''}</div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{dateStr} {m.unit_price ? `@ €${m.unit_price.toFixed(2)}/u` : ''}</div>
                        </div>
                      </div>
                      <div style={{ fontWeight: 600, color: isBuy ? 'var(--color-danger)' : 'var(--color-success)' }}>
                        {isBuy ? '-' : '+'}€{m.amount.toFixed(2)}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
