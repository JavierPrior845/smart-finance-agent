import { useState, useEffect } from 'react';
import { Plus, X, Loader2 } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Budgets() {
  const [budgets, setBudgets] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();

  const [formData, setFormData] = useState({
    category_id: '',
    monthly_limit: ''
  });

  const fetchData = async () => {
    try {
      setLoading(true);
      const [budgetsRes, categoriesRes] = await Promise.all([
        api.get(`/budgets?month=${currentMonth}&year=${currentYear}`),
        api.get('/categories')
      ]);
      setBudgets(budgetsRes.data);
      setCategories(categoriesRes.data);
    } catch (error) {
      console.error("Error fetching budgets data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateBudget = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.category_id || !formData.monthly_limit) return;
    
    setSaving(true);
    try {
      await api.post('/budgets', {
        category_id: formData.category_id,
        monthly_limit: parseFloat(formData.monthly_limit),
        period_month: currentMonth,
        period_year: currentYear
      });
      setShowModal(false);
      setFormData({ category_id: '', monthly_limit: '' });
      await fetchData();
    } catch (error) {
      console.error("Error creating budget", error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Presupuestos</h1>
          <p className="page-subtitle">Control de límites por categoría</p>
        </div>
        <button className="glass-button primary" onClick={() => setShowModal(true)}>
          <Plus size={18} />
          Nuevo Presupuesto
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div className="budget-list">
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
              <Loader2 className="spin" size={32} />
            </div>
          ) : budgets.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>No hay presupuestos definidos para este mes.</p>
          ) : (
            budgets.map(budget => {
              const percent = Math.min((budget.spent / budget.monthly_limit) * 100, 100);
              const isOver = budget.spent > budget.monthly_limit;
              const color = budget.category_color || 'var(--color-primary)';
              
              return (
                <div key={budget.id} className="budget-item">
                  <div className="budget-info">
                    <h4>{budget.category_name}</h4>
                    <span>€{budget.spent.toFixed(2)} / €{budget.monthly_limit.toFixed(2)}</span>
                  </div>
                  <div className="progress-bg">
                    <div 
                      className="progress-fill" 
                      style={{ 
                        width: `${percent}%`, 
                        background: isOver ? 'var(--color-danger)' : color 
                      }}
                    />
                  </div>
                  {isOver && <span className="budget-alert">¡Límite excedido!</span>}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Modal Nuevo Presupuesto */}
      {showModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Fijar Límite Mensual</h3>
              <button onClick={() => setShowModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCreateBudget} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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

              <div className="input-group">
                <label>Límite Mensual (€)</label>
                <input 
                  type="number" 
                  step="0.01"
                  required
                  value={formData.monthly_limit} 
                  onChange={e => setFormData({...formData, monthly_limit: e.target.value})}
                  placeholder="Ej. 200"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <button 
                type="submit" 
                className="glass-button primary" 
                style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }}
                disabled={saving}
              >
                {saving ? <Loader2 className="spin" size={20} /> : 'Guardar Presupuesto'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
