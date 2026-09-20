import React, { useState, useEffect } from 'react';
import { Key, Target, Loader2, Save, Trash2, Plus, X, Shield, Users, UserPlus, Mail, Lock, User as UserIcon } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './Pages.css';

interface InstanceUser {
  id: string;
  name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at?: string;
  last_login_at?: string;
}

export default function Settings() {
  const { user: currentUser } = useAuth();
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

  // States for User Management (Admin Only)
  const [users, setUsers] = useState<InstanceUser[]>([]);
  const [usersLoading, setUsersLoading] = useState(true);
  const [showUserModal, setShowUserModal] = useState(false);
  const [userData, setUserData] = useState({ name: '', email: '', password: '' });
  const [creatingUser, setCreatingUser] = useState(false);

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

    const fetchUsers = async () => {
      if (currentUser?.role === 'admin') {
        try {
          const res = await api.get('/auth/users');
          setUsers(res.data);
        } catch (err) {
          console.error("Error al cargar lista de usuarios", err);
        } finally {
          setUsersLoading(false);
        }
      }
    };

    fetchData();
    fetchUsers();
  }, [currentUser]);

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

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userData.name || !userData.email || !userData.password) return;
    setCreatingUser(true);
    try {
      const res = await api.post('/auth/users', userData);
      setUsers([...users, res.data]);
      setUserData({ name: '', email: '', password: '' });
      setShowUserModal(false);
      toast.success(`Usuario ${res.data.name} creado correctamente`);
    } catch (err) {
      console.error("Error al crear usuario", err);
    } finally {
      setCreatingUser(false);
    }
  };

  const handleDeleteUser = async (userId: string, userName: string) => {
    if (!confirm(`¿Estás seguro de que deseas eliminar al usuario "${userName}"?`)) return;
    try {
      await api.delete(`/auth/users/${userId}`);
      setUsers(users.filter(u => u.id !== userId));
      toast.success(`Usuario "${userName}" eliminado`);
    } catch (err) {
      console.error("Error al eliminar usuario", err);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Configuración</h1>
          <p className="page-subtitle">Gestiona usuarios, automatizaciones y ajustes del sistema</p>
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

      {/* Sección Gestión de Usuarios (Self-Hosted Admin Control) */}
      {currentUser?.role === 'admin' && (
        <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                <Users size={20} /> Usuarios y Accesos a la Instancia
              </h3>
              <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Como administrador, puedes invitar a otros miembros o crear cuentas secundarias de forma privada.
              </p>
            </div>
            <button className="glass-button primary" onClick={() => setShowUserModal(true)}>
              <UserPlus size={18} style={{ marginRight: '6px' }} /> Nuevo Usuario
            </button>
          </div>

          {usersLoading ? (
            <div style={{ display: 'flex', justifyContent: 'center', padding: '24px' }}>
              <Loader2 className="spin" size={24} />
            </div>
          ) : users.length === 0 ? (
            <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>No hay usuarios adicionales registrados.</p>
          ) : (
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Nombre</th>
                    <th>Correo Electrónico</th>
                    <th>Rol</th>
                    <th>Estado</th>
                    <th>Último Acceso</th>
                    <th style={{ textAlign: 'right' }}>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td style={{ fontWeight: 600 }}>{u.name}</td>
                      <td>{u.email}</td>
                      <td>
                        <span
                          className="cat-badge"
                          style={{
                            backgroundColor: u.role === 'admin' ? 'rgba(138, 43, 226, 0.25)' : 'rgba(0, 245, 212, 0.2)',
                            color: u.role === 'admin' ? 'var(--color-primary-light)' : 'var(--color-secondary)',
                            border: `1px solid ${u.role === 'admin' ? 'var(--color-primary)' : 'var(--color-secondary)'}`
                          }}
                        >
                          {u.role.toUpperCase()}
                        </span>
                      </td>
                      <td>
                        <span style={{ color: u.is_active ? 'var(--color-success)' : 'var(--color-danger)', fontSize: '0.85rem' }}>
                          {u.is_active ? '● Activo' : '○ Inactivo'}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        {u.last_login_at ? new Date(u.last_login_at).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'short' }) : 'Nunca'}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        {u.id !== currentUser.id ? (
                          <button
                            onClick={() => handleDeleteUser(u.id, u.name)}
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: 'var(--color-danger)',
                              cursor: 'pointer',
                              opacity: 0.8
                            }}
                            title="Eliminar Usuario"
                          >
                            <Trash2 size={16} />
                          </button>
                        ) : (
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>(Tu cuenta)</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      <div className="glass-panel" style={{ padding: '24px', marginTop: '24px' }}>
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

      {/* Modal Nuevo Usuario (Admin Only) */}
      {showUserModal && (
        <div className="modal-overlay" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)',
          display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, backdropFilter: 'blur(4px)'
        }}>
          <div className="glass-panel" style={{ width: '420px', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Shield size={20} /> Crear Usuario de Acceso
              </h3>
              <button onClick={() => setShowUserModal(false)} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer' }}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleCreateUser} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="input-group">
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <UserIcon size={15} /> Nombre Completo
                </label>
                <input
                  type="text"
                  required
                  placeholder="Ej. Nombre Familiar / Pareja"
                  value={userData.name}
                  onChange={e => setUserData({ ...userData, name: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Mail size={15} /> Correo Electrónico
                </label>
                <input
                  type="email"
                  required
                  placeholder="usuario@smartfinance.local"
                  value={userData.email}
                  onChange={e => setUserData({ ...userData, email: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <div className="input-group">
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Lock size={15} /> Contraseña de Acceso
                </label>
                <input
                  type="password"
                  required
                  minLength={6}
                  placeholder="Mínimo 6 caracteres"
                  value={userData.password}
                  onChange={e => setUserData({ ...userData, password: e.target.value })}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              <button type="submit" className="glass-button primary" style={{ marginTop: '10px', display: 'flex', justifyContent: 'center' }} disabled={creatingUser}>
                {creatingUser ? <Loader2 className="spin" size={20} /> : 'Crear Usuario'}
              </button>
            </form>
          </div>
        </div>
      )}

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
