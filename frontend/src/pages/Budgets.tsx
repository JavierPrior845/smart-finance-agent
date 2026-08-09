import { useState, useEffect } from 'react';
import { Plus, X, Loader2, Trash2, Edit2 } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Budgets() {
  const [budgets, setBudgets] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [saving, setSaving] = useState(false);
  
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();

  const [overrideData, setOverrideData] = useState({ category_id: '', monthly_limit: '' });
  const [categoryData, setCategoryData] = useState({ name: '', color: '#3b82f6', default_budget_limit: '' });

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
      console.error("Error fetching data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideData.category_id || !overrideData.monthly_limit) return;
    setSaving(true);
    try {
      await api.post('/budgets', {
        category_id: overrideData.category_id,
        monthly_limit: parseFloat(overrideData.monthly_limit),
        period_month: currentMonth,
        period_year: currentYear
      });
      setShowOverrideModal(false);
      setOverrideData({ category_id: '', monthly_limit: '' });
      await fetchData();
    } catch (error) {
      console.error("Error creating override", error);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!categoryData.name) return;
    setSaving(true);
    try {
      await api.post('/categories', {
        name: categoryData.name,
        color: categoryData.color,
        is_budgetable: true,
        default_budget_limit: categoryData.default_budget_limit ? parseFloat(categoryData.default_budget_limit) : null,
        is_active: true
      });
      setShowCategoryModal(false);
      setCategoryData({ name: '', color: '#3b82f6', default_budget_limit: '' });
      await fetchData();
    } catch (error) {
      console.error("Error creating category", error);
    } finally {
      setSaving(false);
    }
  };

  const handleDeactivateCategory = async (categoryId: string) => {
    if (!confirm("¿Seguro que quieres desactivar esta categoría? Ya no aparecerá en tus presupuestos.")) return;
    try {
      await api.put(`/categories/${categoryId}`, { is_active: false });
      await fetchData();
    } catch (error) {
      console.error("Error deactivating category", error);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Presupuestos y Categorías</h1>
          <p className="page-subtitle">Gestiona tus límites genéricos y ajustes mensuales</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="glass-button" onClick={() => setShowCategoryModal(true)}>
            <Plus size={18} />
            Nueva Categoría
          </button>
          <button className="glass-button primary" onClick={() => setShowOverrideModal(true)}>
            <Edit2 size={18} />
            Ajustar este Mes
          </button>
        </div>
      </div>

      <div className="responsive-grid">
        {/* Columna Izquierda: Progreso del Mes */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Progreso de este Mes</h3>
          <div className="budget-list">
            {loading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                <Loader2 className="spin" size={32} />
              </div>
            ) : budgets.length === 0 ? (
              <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>No hay presupuestos activos este mes.</p>
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
                        style={{ width: `${percent}%`, background: isOver ? 'var(--color-danger)' : color }}
                      />
                    </div>
                    {isOver && <span className="budget-alert">¡Límite excedido!</span>}
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Columna Derecha: Todas las categorías */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Tus Categorías Base</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {categories.map(cat => (
              <div key={cat.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ width: '16px', height: '16px', borderRadius: '50%', backgroundColor: cat.color || '#ccc' }}></div>
                  <div>
                    <h4 style={{ margin: 0 }}>{cat.name}</h4>
                    <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {cat.default_budget_limit ? `Límite Base: €${cat.default_budget_limit}` : 'Sin límite genérico'}
                    </span>
                  </div>
                </div>
                <button 
                  onClick={() => handleDeactivateCategory(cat.id)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--color-danger)', cursor: 'pointer', opacity: 0.8 }}
                  title="Desactivar Categoría"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Modal Ajuste Mensual (Override) */}
      {showOverrideModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Excepción de este Mes</h3>
              <button onClick={() => setShowOverrideModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
              Si configuras un límite aquí, sobrescribirá el genérico para este mes. Escribe 0 si quieres desactivarlo este mes.
            </p>
            <form onSubmit={handleCreateOverride} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label>Categoría</label>
                <select 
                  required
                  value={overrideData.category_id} 
                  onChange={e => setOverrideData({...overrideData, category_id: e.target.value})}
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
                  value={overrideData.monthly_limit} 
                  onChange={e => setOverrideData({...overrideData, monthly_limit: e.target.value})}
                  placeholder="Ej. 200 (o 0 para ocultar)"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <button type="submit" className="glass-button primary" style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }} disabled={saving}>
                {saving ? <Loader2 className="spin" size={20} /> : 'Guardar Ajuste'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Modal Nueva Categoría */}
      {showCategoryModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Nueva Categoría Base</h3>
              <button onClick={() => setShowCategoryModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCreateCategory} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label>Nombre de la Categoría</label>
                <input 
                  type="text" 
                  required
                  value={categoryData.name} 
                  onChange={e => setCategoryData({...categoryData, name: e.target.value})}
                  placeholder="Ej. Financiación Móvil"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label>Límite Genérico al Mes (€) - Opcional</label>
                <input 
                  type="number" 
                  step="0.01"
                  value={categoryData.default_budget_limit} 
                  onChange={e => setCategoryData({...categoryData, default_budget_limit: e.target.value})}
                  placeholder="Ej. 50"
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
              
              <div className="input-group">
                <label>Color</label>
                <input 
                  type="color" 
                  required
                  value={categoryData.color} 
                  onChange={e => setCategoryData({...categoryData, color: e.target.value})}
                  style={{ width: '100%', height: '40px', padding: '2px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <button type="submit" className="glass-button primary" style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }} disabled={saving}>
                {saving ? <Loader2 className="spin" size={20} /> : 'Crear Categoría'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
