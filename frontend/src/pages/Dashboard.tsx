import { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownRight, Activity, X, Loader2, AlertTriangle } from 'lucide-react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, 
  BarChart, Bar, LineChart, Line, AreaChart, Area, 
  XAxis, YAxis, CartesianGrid, Legend 
} from 'recharts';
import api from '../services/api';
import './Pages.css';

export default function Dashboard() {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  // States for dynamic data
  const [loading, setLoading] = useState(true);
  const [kpis, setKpis] = useState({ net_worth: 0, monthly_income: 0, monthly_expenses: 0, savings_rate: 0, income_trend: null as number | null, expenses_trend: null as number | null, net_worth_trend: null as number | null, target_savings_rate: 50.0 });
  const [distributionData, setDistributionData] = useState<any[]>([]);
  const [cashFlowData, setCashFlowData] = useState<any[]>([]);
  const [pacingData, setPacingData] = useState<any[]>([]);
  const [netWorthData, setNetWorthData] = useState<any[]>([]);
  const [syncingInvestments, setSyncingInvestments] = useState(false);
  const [anomalies, setAnomalies] = useState<any[]>([]);

  const [showModal, setShowModal] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    type: 'EXPENSE',
    category_id: '',
    account_id: ''
  });
  const [savingTx, setSavingTx] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [kpiRes, distRes, flowRes, pacingRes, netWorthRes, catRes, accRes, anomalyRes] = await Promise.all([
        api.get('/analytics/kpis'),
        api.get('/analytics/distribution'),
        api.get('/analytics/cashflow'),
        api.get('/analytics/pacing'),
        api.get('/analytics/networth'),
        api.get('/categories'),
        api.get('/accounts'),
        api.get('/analytics/anomalies')
      ]);
      
      setKpis(kpiRes.data);
      setDistributionData(distRes.data.data);
      setCashFlowData(flowRes.data.data);
      setPacingData(pacingRes.data.data);
      setNetWorthData(netWorthRes.data.data);
      setCategories(catRes.data);
      setAccounts(accRes.data);
      setAnomalies(anomalyRes.data);
    } catch (error) {
      console.error("Error fetching dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  const syncInvestments = async () => {
    try {
      setSyncingInvestments(true);
      await api.post('/investments/sync');
      // Refetch data after sync to get updated net worth
      await fetchData();
    } catch (error) {
      console.error("Error syncing investments", error);
    } finally {
      setSyncingInvestments(false);
    }
  };

  useEffect(() => {
    fetchData();
    syncInvestments(); // Silent sync in background
  }, []);

  const handleCreateTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.amount || !formData.description) return;
    
    setSavingTx(true);
    try {
      await api.post('/transactions', {
        type: formData.type,
        amount: parseFloat(formData.amount),
        description: formData.description,
        category_id: formData.category_id || null,
        account_id: formData.account_id || null,
        transaction_date: new Date().toISOString(),
        source: 'manual'
      });
      setShowModal(false);
      setFormData({ amount: '', description: '', type: 'EXPENSE', category_id: '', account_id: '' });
      await fetchData(); // Reload dashboard data
    } catch (error) {
      console.error("Error creating transaction", error);
    } finally {
      setSavingTx(false);
    }
  };

  const handlePieClick = (data: any) => {
    setSelectedCategory(prev => prev === data.name ? null : data.name);
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            Dashboard
            {syncingInvestments && <span title="Sincronizando inversiones..."><Loader2 className="spin" size={20} style={{ color: 'var(--color-primary)' }} /></span>}
          </h1>
          <p className="page-subtitle">Visión general de tus finanzas</p>
        </div>
        <button className="glass-button primary" onClick={() => setShowModal(true)}>
          + Nuevo Gasto
        </button>
      </div>

      {loading ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px' }}>
          <Loader2 size={48} className="spin" style={{ color: 'var(--color-primary)' }} />
        </div>
      ) : (
        <>
          <div className="kpi-grid">
            <div className="glass-panel kpi-card">
              <span className="kpi-title">Patrimonio Total</span>
              <span className="kpi-value">€{kpis.net_worth.toFixed(2)}</span>
              <div className="kpi-trend">
                <span>Liquidez (excl. inversiones)</span>
              </div>
            </div>
            <div className="glass-panel kpi-card">
              <span className="kpi-title">Ingresos Mensuales</span>
              <span className="kpi-value text-success">€{kpis.monthly_income.toFixed(2)}</span>
              {kpis.income_trend !== null && (
                <div className={`kpi-trend ${kpis.income_trend >= 0 ? 'positive' : 'negative'}`}>
                  {kpis.income_trend >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
                  <span>{Math.abs(kpis.income_trend).toFixed(1)}% vs anterior</span>
                </div>
              )}
            </div>
            <div className="glass-panel kpi-card">
              <span className="kpi-title">Gastos Mensuales</span>
              <span className="kpi-value text-danger">€{kpis.monthly_expenses.toFixed(2)}</span>
              {kpis.expenses_trend !== null && (
                <div className={`kpi-trend ${kpis.expenses_trend <= 0 ? 'positive' : 'negative'}`}>
                  {kpis.expenses_trend <= 0 ? <ArrowDownRight size={16} /> : <ArrowUpRight size={16} />}
                  <span>{Math.abs(kpis.expenses_trend).toFixed(1)}% vs anterior</span>
                </div>
              )}
            </div>
            <div className="glass-panel kpi-card">
              <span className="kpi-title">Tasa de Ahorro</span>
              <span className="kpi-value">{kpis.savings_rate.toFixed(1)}%</span>
              <div className="kpi-trend">
                <Activity size={16} />
                <span>Objetivo: {kpis.target_savings_rate}%</span>
              </div>
            </div>
          </div>

          {anomalies.length > 0 && (
            <div className="glass-panel" style={{ padding: '20px', marginTop: '24px', border: '1px solid rgba(255, 71, 87, 0.3)', background: 'rgba(255, 71, 87, 0.03)' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-danger)', margin: '0 0 12px 0', fontSize: '1.1rem' }}>
                <AlertTriangle size={18} /> Alertas de Anomalías (Gastos Atípicos Detectados)
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {anomalies.map((tx) => {
                  const cat = categories.find(c => c.id === tx.category_id);
                  return (
                    <div key={tx.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderRadius: '8px', background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-glass)' }}>
                      <div>
                        <div style={{ fontWeight: '600', color: '#fff' }}>{tx.description}</div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                          <span>{new Date(tx.transaction_date).toLocaleDateString()}</span>
                          {cat && (
                            <span className="cat-badge" style={{ backgroundColor: `${cat.color}22`, color: cat.color, border: `1px solid ${cat.color}33`, padding: '2px 6px', fontSize: '0.75rem' }}>
                              {cat.name}
                            </span>
                          )}
                          <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem' }}>Importe supera el comportamiento de gasto típico</span>
                        </div>
                      </div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--color-danger)' }}>
                        -€{Math.abs(tx.amount).toFixed(2)}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

      <div className="charts-grid">
        {/* COLUMNA IZQUIERDA */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Evolución del Patrimonio Neto */}
          <div className="glass-panel" style={{ padding: '24px', flex: 1, minHeight: '300px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>Evolución del Patrimonio Neto</h3>
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={netWorthData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorLiquidez" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00f5d4" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#00f5d4" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorInversiones" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8a2be2" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8a2be2" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="month" stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                <YAxis stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                <Tooltip contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-glass)', borderRadius: '8px', color: '#fff' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="liquidez" name="Liquidez" stackId="1" stroke="#00f5d4" fill="url(#colorLiquidez)" />
                <Area type="monotone" dataKey="inversiones" name="Inversiones" stackId="1" stroke="#8a2be2" fill="url(#colorInversiones)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Cash Flow Histórico */}
          <div className="glass-panel" style={{ padding: '24px', flex: 1, minHeight: '300px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>Cash Flow Histórico</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={cashFlowData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="month" stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                <YAxis stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                <Tooltip 
                  cursor={{fill: 'rgba(255,255,255,0.05)'}}
                  contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-glass)', borderRadius: '8px', color: '#fff' }} 
                />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="ingresos" name="Ingresos" fill="#00f5d4" radius={[4, 4, 0, 0]} />
                <Bar dataKey="gastos" name="Gastos" fill="#ff4757" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

        </div>

        {/* COLUMNA DERECHA */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Ritmo de Gasto Acumulado */}
          <div className="glass-panel" style={{ padding: '24px', flex: 1, minHeight: '300px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>Ritmo de Gasto (Pacing)</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={pacingData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                <XAxis dataKey="day" stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                <YAxis stroke="var(--text-muted)" tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                <Tooltip contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-glass)', borderRadius: '8px', color: '#fff' }} />
                <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="mesAnterior" name="Mes Anterior" stroke="#636e72" strokeWidth={2} dot={false} strokeDasharray="5 5" />
                <Line type="monotone" dataKey="mesActual" name="Mes Actual" stroke="#1e90ff" strokeWidth={3} dot={{r: 4, fill: '#1e90ff', strokeWidth: 0}} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Distribución de Gastos (Interactivo) */}
          <div className="glass-panel" style={{ padding: '24px', flex: 1, minHeight: '300px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>
              Distribución de Gastos {selectedCategory && <span className="cat-badge" style={{ marginLeft: '12px' }}>{selectedCategory} <X size={12} style={{ display: 'inline', cursor: 'pointer', marginLeft: '4px' }} onClick={() => setSelectedCategory(null)} /></span>}
            </h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie
                  data={distributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                  onClick={handlePieClick}
                  style={{ cursor: 'pointer' }}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  labelLine={{ stroke: 'rgba(255,255,255,0.2)' }}
                >
                  {distributionData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color} 
                      opacity={selectedCategory && selectedCategory !== entry.name ? 0.3 : 1}
                      style={{ transition: 'opacity 0.3s ease' }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        </div>
        </>
      )}

      {/* Modal Nueva Transacción */}
      {showModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Nueva Transacción</h3>
              <button onClick={() => setShowModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCreateTransaction} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label>Tipo</label>
                <select 
                  value={formData.type} 
                  onChange={e => setFormData({...formData, type: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="EXPENSE">Gasto</option>
                  <option value="INCOME">Ingreso</option>
                </select>
              </div>
              
              <div className="input-group">
                <label>Cantidad (€)</label>
                <input 
                  type="number" 
                  step="0.01"
                  required
                  value={formData.amount} 
                  onChange={e => setFormData({...formData, amount: e.target.value})}
                  placeholder="Ej. 45.50"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label>Descripción</label>
                <input 
                  type="text" 
                  required
                  value={formData.description} 
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  placeholder="Ej. Cena restaurante"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label>Categoría (Opcional)</label>
                <select 
                  value={formData.category_id} 
                  onChange={e => setFormData({...formData, category_id: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">(Sin categoría - irá a Otros)</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className="input-group">
                <label>Cuenta (Opcional)</label>
                <select 
                  value={formData.account_id} 
                  onChange={e => setFormData({...formData, account_id: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">(Cuenta principal por defecto)</option>
                  {accounts.map(acc => (
                    <option key={acc.id} value={acc.id}>{acc.name} {acc.is_main ? '(Principal)' : ''}</option>
                  ))}
                </select>
              </div>

              <button 
                type="submit" 
                className="glass-button primary" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}
                disabled={savingTx}
              >
                {savingTx ? <Loader2 className="spin" size={20} /> : 'Guardar'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
