import { useState, useEffect } from 'react';
import { ArrowUpRight, ArrowDownRight, Activity, X, Loader2 } from 'lucide-react';
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
  
  // Note: Net worth historical is mocked for now until Subtask 2.5 is completed
  const netWorthData = [
    { month: 'May', liquidez: 4000, inversiones: 6000 },
    { month: 'Jun', liquidez: 4200, inversiones: 6300 },
    { month: 'Jul', liquidez: 3500, inversiones: 6800 },
    { month: 'Ago', liquidez: 4500, inversiones: 7100 },
    { month: 'Sep', liquidez: 5100, inversiones: 7000 },
    { month: 'Oct', liquidez: 5350, inversiones: 7100 },
  ];

  const [showModal, setShowModal] = useState(false);
  const [categories, setCategories] = useState<any[]>([]);
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    type: 'EXPENSE',
    category_id: ''
  });
  const [savingTx, setSavingTx] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [kpiRes, distRes, flowRes, pacingRes, catRes] = await Promise.all([
        api.get('/analytics/kpis'),
        api.get('/analytics/distribution'),
        api.get('/analytics/cashflow'),
        api.get('/analytics/pacing'),
        api.get('/categories')
      ]);
      
      setKpis(kpiRes.data);
      setDistributionData(distRes.data.data);
      setCashFlowData(flowRes.data.data);
      setPacingData(pacingRes.data.data);
      setCategories(catRes.data);
    } catch (error) {
      console.error("Error fetching dashboard data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateTransaction = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.amount || !formData.description || !formData.category_id) return;
    
    setSavingTx(true);
    try {
      await api.post('/transactions', {
        amount: parseFloat(formData.amount),
        description: formData.description,
        type: formData.type,
        category_id: formData.category_id,
        transaction_date: new Date().toISOString(),
        source: 'manual'
      });
      setShowModal(false);
      setFormData({ amount: '', description: '', type: 'EXPENSE', category_id: '' });
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
          <h1 className="page-title">Dashboard</h1>
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
                <label>Categoría</label>
                <select 
                  required
                  value={formData.category_id} 
                  onChange={e => setFormData({...formData, category_id: e.target.value})}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">Selecciona una categoría...</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
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
