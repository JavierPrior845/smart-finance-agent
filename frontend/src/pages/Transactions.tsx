import { useState, useEffect, useCallback } from 'react';
import { X, Loader2 } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Transactions() {
  const [transactions, setTransactions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Pagination State
  const [page, setPage] = useState(1);
  const limit = 20;
  const [total, setTotal] = useState(0);
  
  // Filter State
  const [search, setSearch] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [source, setSource] = useState('');

  // Dropdown data
  const [categories, setCategories] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);

  // Modal State
  const [showModal, setShowModal] = useState(false);
  const [savingTx, setSavingTx] = useState(false);
  const [formData, setFormData] = useState({
    amount: '',
    description: '',
    type: 'EXPENSE',
    category_id: '',
    account_id: ''
  });

  const fetchFiltersData = async () => {
    try {
      const [catRes, accRes] = await Promise.all([
        api.get('/categories'),
        api.get('/accounts')
      ]);
      setCategories(catRes.data);
      setAccounts(accRes.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchTransactions = useCallback(async () => {
    try {
      setLoading(true);
      const offset = (page - 1) * limit;
      let url = `/transactions?limit=${limit}&offset=${offset}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      if (categoryId) url += `&category_id=${categoryId}`;
      if (source) url += `&source=${source}`;
      
      const res = await api.get(url);
      setTransactions(res.data.items);
      setTotal(res.data.total);
    } catch (error) {
      console.error("Error fetching transactions", error);
    } finally {
      setLoading(false);
    }
  }, [page, limit, search, categoryId, source]);

  useEffect(() => {
    fetchFiltersData();
  }, []);

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const handleApplyFilters = () => {
    setPage(1);
    fetchTransactions();
  };

  const handleClearFilters = () => {
    setSearch('');
    setCategoryId('');
    setSource('');
    setPage(1);
    // Note: React state updates are batched, fetchTransactions will be called by useEffect
  };

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
      setPage(1);
      fetchTransactions();
    } catch (error) {
      console.error("Error creating transaction", error);
    } finally {
      setSavingTx(false);
    }
  };

  const getCategoryName = (id: string | null) => {
    if (!id) return 'Otros';
    const cat = categories.find(c => c.id === id);
    return cat ? cat.name : 'Otros';
  };

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Histórico de Transacciones</h1>
          <p className="page-subtitle">Registro detallado de movimientos</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <div className="page-controls">
            <button className="glass-button primary" onClick={() => setShowModal(true)}>+ Añadir Transacción</button>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '16px 24px', marginBottom: '-16px' }}>
        <div className="filters-bar">
          <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
            <label>Buscar</label>
            <input 
              type="text" 
              placeholder="Concepto, comercio..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleApplyFilters()}
            />
          </div>
          <div className="input-group" style={{ minWidth: '150px' }}>
            <label>Categoría</label>
            <select value={categoryId} onChange={e => setCategoryId(e.target.value)}>
              <option value="">Todas</option>
              {categories.map(c => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
          <div className="input-group" style={{ minWidth: '150px' }}>
            <label>Fuente</label>
            <select value={source} onChange={e => setSource(e.target.value)}>
              <option value="">Todas</option>
              <option value="telegram">Telegram</option>
              <option value="manual">Manual</option>
              <option value="SEED">Semilla (SEED)</option>
            </select>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end', alignSelf: 'stretch', paddingBottom: '2px' }}>
            <button className="glass-button primary" style={{ height: '38px', marginTop: 'auto' }} onClick={handleApplyFilters}>Aplicar</button>
            <button className="glass-button" style={{ height: '38px', marginTop: 'auto' }} onClick={handleClearFilters}>Limpiar</button>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div className="table-responsive">
          <table className="data-table full-width">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Descripción</th>
                <th>Categoría</th>
                <th>Fuente</th>
                <th style={{ textAlign: 'right' }}>Importe</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '40px' }}>
                    <Loader2 size={32} className="spin" style={{ margin: '0 auto', color: 'var(--color-primary)' }} />
                  </td>
                </tr>
              ) : transactions.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px' }}>
                    No se encontraron transacciones.
                  </td>
                </tr>
              ) : (
                transactions.map(txn => {
                  const dateStr = new Date(txn.transaction_date).toLocaleDateString();
                  return (
                    <tr key={txn.id}>
                      <td style={{ color: 'var(--text-secondary)' }}>{dateStr}</td>
                      <td><strong>{txn.description}</strong></td>
                      <td><span className="cat-badge">{getCategoryName(txn.category_id)}</span></td>
                      <td style={{ color: 'var(--text-secondary)' }}>{txn.source}</td>
                      <td style={{ textAlign: 'right' }} className={txn.amount > 0 ? 'text-success' : 'text-primary'}>
                        {txn.amount > 0 ? '+' : ''}€{Math.abs(txn.amount).toFixed(2)}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
        
        <div className="pagination">
          <span>Mostrando {total === 0 ? 0 : (page - 1) * limit + 1}-{Math.min(page * limit, total)} de {total}</span>
          <div className="page-controls">
            <button 
              className="glass-button" 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              &lt;
            </button>
            <span style={{ margin: '0 10px' }}>{page} / {totalPages || 1}</span>
            <button 
              className="glass-button" 
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
            >
              &gt;
            </button>
          </div>
        </div>
      </div>

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
