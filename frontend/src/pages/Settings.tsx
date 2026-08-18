import { useState, useEffect } from 'react';
import { Key, Target, Loader2, Save, Trash2, Plus, X } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Settings() {
  const [targetSavingsRate, setTargetSavingsRate] = useState<string>("50.0");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // States for Merchant Rules
  const [rules, setRules] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [rulesLoading, setRulesLoading] = useState(true);
  const [showRuleModal, setShowRuleModal] = useState(false);
  const [ruleData, setRuleData] = useState({ pattern: '', category_id: '', priority: '1' });
  const [creatingRule, setCreatingRule] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [settingsRes, rulesRes, categoriesRes] = await Promise.all([
          api.get('/settings/target_savings_rate'),
          api.get('/settings/merchant-rules'),
          api.get('/categories')
        ]);
        setTargetSavingsRate(settingsRes.data.value);
        setRules(rulesRes.data);
        setCategories(categoriesRes.data);
      } catch (err) {
        console.error("Error al cargar datos de configuración", err);
      } finally {
        setLoading(false);
        setRulesLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSaveSavingsRate = async () => {
    setSaving(true);
    try {
      await api.put('/settings/target_savings_rate', {
        value: targetSavingsRate,
        description: "Tasa de ahorro objetivo (%)"
      });
    } catch (err) {
      console.error("Error al guardar la tasa de ahorro", err);
    } finally {
      setSaving(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ruleData.pattern || !ruleData.category_id) return;
    setCreatingRule(true);
    try {
      const res = await api.post('/settings/merchant-rules', {
        pattern: ruleData.pattern,
        category_id: ruleData.category_id,
        priority: parseInt(ruleData.priority) || 1
      });
      setRules([res.data, ...rules]);
      setRuleData({ pattern: '', category_id: '', priority: '1' });
      setShowRuleModal(false);
    } catch (err) {
      console.error("Error al crear regla de comercio", err);
    } finally {
      setCreatingRule(false);
    }
  };

  const handleDeleteRule = async (id: string) => {
    if (!confirm("¿Seguro que quieres eliminar esta regla de categorización?")) return;
    try {
      await api.delete(`/settings/merchant-rules/${id}`);
      setRules(rules.filter(r => r.id !== id));
    } catch (err) {
      console.error("Error al eliminar la regla", err);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Configuración</h1>
          <p className="page-subtitle">Gestiona automatizaciones y ajustes del sistema</p>
        </div>
      </div>

      <div className="accounts-grid">
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Key size={20} /> Conexión con Telegram
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="input-group">
              <label>Bot Token</label>
              <input type="password" placeholder="123456789:AAH..." defaultValue="mock-token-abc" />
            </div>
            <div className="input-group">
              <label>ID Usuario Permitido</label>
              <input type="text" placeholder="ID numérico de Telegram" defaultValue="987654321" />
            </div>
            <button className="glass-button primary" style={{ alignSelf: 'flex-start' }}>Guardar Tokens</button>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={20} /> Objetivos Financieros
          </h3>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
              <Loader2 className="spin" size={24} />
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label>Tasa de Ahorro Objetivo (%)</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <input
                    type="number"
                    value={targetSavingsRate}
                    onChange={(e) => setTargetSavingsRate(e.target.value)}
                    style={{ flex: 1 }}
                  />
                  <button
                    className="glass-button primary"
                    onClick={handleSaveSavingsRate}
                    disabled={saving}
                  >
                    {saving ? <Loader2 className="spin" size={16} /> : <Save size={16} />}
                  </button>
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Este valor se usará para calcular el cumplimiento en tu Dashboard.</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h3>Reglas de Categorización (Comercios)</h3>
          <button className="glass-button" onClick={() => setShowRuleModal(true)}>
            <Plus size={18} style={{ marginRight: '6px' }} /> Nueva Regla
          </button>
        </div>

        {rulesLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '24px' }}>
            <Loader2 className="spin" size={24} />
          </div>
        ) : rules.length === 0 ? (
          <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>No hay reglas de categorización configuradas.</p>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Patrón de Búsqueda (Texto/Regex)</th>
                  <th>Categoría a Asignar</th>
                  <th>Prioridad</th>
                  <th style={{ textAlign: 'right' }}>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {rules.map(rule => {
                  const category = categories.find(c => c.id === rule.category_id);
                  return (
                    <tr key={rule.id}>
                      <td><code>{rule.pattern}</code></td>
                      <td>
                        <span
                          className="cat-badge"
                          style={{
                            backgroundColor: category?.color ? `${category.color}33` : 'rgba(255,255,255,0.1)',
                            color: category?.color || '#fff',
                            border: `1px solid ${category?.color || 'rgba(255,255,255,0.2)'}`
                          }}
                        >
                          {category?.name || 'Desconocida'}
                        </span>
                      </td>
                      <td>{rule.priority}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--color-danger)',
                            cursor: 'pointer',
                            opacity: 0.8
                          }}
                          title="Eliminar Regla"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal Nueva Regla */}
      {showRuleModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '400px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Nueva Regla de Categorización</h3>
              <button onClick={() => setShowRuleModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateRule} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label>Patrón de Búsqueda (Texto o Regex)</label>
                <input
                  type="text"
                  required
                  placeholder="Ej. MERCADONA o Uber.*"
                  value={ruleData.pattern}
                  onChange={e => setRuleData({ ...ruleData, pattern: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label>Categoría a Asignar</label>
                <select
                  required
                  value={ruleData.category_id}
                  onChange={e => setRuleData({ ...ruleData, category_id: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                >
                  <option value="">Selecciona una categoría...</option>
                  {categories.map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>

              <div className="input-group">
                <label>Prioridad (Las prioridades más altas se ejecutan primero)</label>
                <input
                  type="number"
                  min="1"
                  required
                  value={ruleData.priority}
                  onChange={e => setRuleData({ ...ruleData, priority: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <button type="submit" className="glass-button primary" style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }} disabled={creatingRule}>
                {creatingRule ? <Loader2 className="spin" size={20} /> : 'Guardar Regla'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
