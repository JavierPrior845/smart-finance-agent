import { useState, useEffect } from 'react';
import { Check, X, Loader2, MessageSquare, ChevronDown, ChevronUp } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';
import './Pages.css';

export default function ValidationInbox() {
  const [pendingTransactions, setPendingTransactions] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actioningId, setActioningId] = useState<string | null>(null);
  const [expandedCardId, setExpandedCardId] = useState<string | null>(null);

  const fetchPendingData = async () => {
    try {
      setLoading(true);
      const [pendingRes, accountsRes, categoriesRes] = await Promise.all([
        api.get('/transactions/pending'),
        api.get('/accounts'),
        api.get('/categories')
      ]);

      const accs = accountsRes.data;
      const cats = categoriesRes.data;

      setAccounts(accs);
      setCategories(cats);

      const mapped = pendingRes.data.map((tx: any) => {
        // Find matching account id
        let accId = '';
        if (tx.account_name) {
          const match = accs.find((a: any) => a.name.toLowerCase() === tx.account_name.toLowerCase());
          if (match) accId = match.id;
          else {
            const fuzzy = accs.find((a: any) => tx.account_name.toLowerCase().includes(a.name.toLowerCase()) || a.name.toLowerCase().includes(tx.account_name.toLowerCase()));
            if (fuzzy) accId = fuzzy.id;
          }
        }

        // Find matching category id
        let catId = '';
        if (tx.category_name) {
          const match = cats.find((c: any) => c.name.toLowerCase() === tx.category_name.toLowerCase());
          if (match) catId = match.id;
          else {
            const fuzzy = cats.find((c: any) => tx.category_name.toLowerCase().includes(c.name.toLowerCase()) || c.name.toLowerCase().includes(tx.category_name.toLowerCase()));
            if (fuzzy) catId = fuzzy.id;
          }
        }

        return {
          ...tx,
          editingDescription: tx.description || '',
          editingAmount: tx.amount !== undefined ? Math.abs(tx.amount).toString() : '0',
          editingType: tx.type || 'EXPENSE',
          editingAccountId: accId || (accs.find((a: any) => a.is_main)?.id || ''),
          editingCategoryId: catId || ''
        };
      });

      setPendingTransactions(mapped);
    } catch (error) {
      console.error("Error fetching pending data", error);
      toast.error("Error al cargar los datos del Inbox");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPendingData();
  }, []);

  const handleFieldChange = (id: string, field: string, value: any) => {
    setPendingTransactions(prev => prev.map(tx => {
      if (tx.id === id) {
        return { ...tx, [field]: value };
      }
      return tx;
    }));
  };

  const handleConfirm = async (txn: any) => {
    if (!txn.editingDescription || !txn.editingAmount) {
      toast.error("Por favor completa concepto e importe.");
      return;
    }

    setActioningId(txn.id);
    try {
      const payload = {
        amount: parseFloat(txn.editingAmount),
        type: txn.editingType,
        description: txn.editingDescription,
        account_id: txn.editingAccountId || null,
        category_id: txn.editingCategoryId || null
      };

      await api.post(`/transactions/pending/${txn.id}/confirm`, payload);
      toast.success("Transacción registrada con éxito");
      
      // Remove from local list
      setPendingTransactions(prev => prev.filter(t => t.id !== txn.id));
    } catch (error: any) {
      console.error("Error confirming transaction", error);
      toast.error(error.response?.data?.detail || "Error al confirmar la transacción");
    } finally {
      setActioningId(null);
    }
  };

  const handleDiscard = async (id: string) => {
    if (!confirm("¿Seguro que deseas descartar este borrador?")) return;

    setActioningId(id);
    try {
      await api.delete(`/transactions/pending/${id}`);
      toast.success("Borrador descartado");
      setPendingTransactions(prev => prev.filter(t => t.id !== id));
    } catch (error) {
      console.error("Error discarding transaction", error);
      toast.toast("Error al descartar la transacción");
    } finally {
      setActioningId(null);
    }
  };

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Inbox de Validación</h1>
          <p className="page-subtitle">Revisa y edita las operaciones extraídas por IA antes de registrarlas</p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
            <Loader2 className="spin" size={36} />
          </div>
        ) : pendingTransactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 40px', color: 'var(--text-muted)' }}>
            <MessageSquare size={54} style={{ opacity: 0.5, marginBottom: '20px' }} />
            <h3>¡Todo al día!</h3>
            <p>No tienes transacciones pendientes de revisión en tu bandeja de entrada.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {pendingTransactions.map(txn => (
              <div key={txn.id} className="glass-panel" style={{ padding: '24px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  
                  {/* Edit Form */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                    
                    <div className="input-group">
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>Concepto</label>
                      <input 
                        type="text" 
                        value={txn.editingDescription} 
                        onChange={e => handleFieldChange(txn.id, 'editingDescription', e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                      />
                    </div>

                    <div style={{ display: 'flex', gap: '12px' }}>
                      <div className="input-group" style={{ flex: 1 }}>
                        <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>Importe (€)</label>
                        <input 
                          type="number" 
                          step="0.01" 
                          value={txn.editingAmount} 
                          onChange={e => handleFieldChange(txn.id, 'editingAmount', e.target.value)}
                          style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                        />
                      </div>
                      <div className="input-group" style={{ width: '110px' }}>
                        <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>Tipo</label>
                        <select 
                          value={txn.editingType} 
                          onChange={e => handleFieldChange(txn.id, 'editingType', e.target.value)}
                          style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                        >
                          <option value="EXPENSE">Gasto</option>
                          <option value="INCOME">Ingreso</option>
                        </select>
                      </div>
                    </div>

                    <div className="input-group">
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>Cuenta Destino</label>
                      <select 
                        value={txn.editingAccountId} 
                        onChange={e => handleFieldChange(txn.id, 'editingAccountId', e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                      >
                        <option value="">Seleccionar cuenta...</option>
                        {accounts.map(a => (
                          <option key={a.id} value={a.id}>{a.name}</option>
                        ))}
                      </select>
                    </div>

                    <div className="input-group">
                      <label style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '6px', display: 'block' }}>Categoría</label>
                      <select 
                        value={txn.editingCategoryId} 
                        onChange={e => handleFieldChange(txn.id, 'editingCategoryId', e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)' }}
                      >
                        <option value="">Seleccionar categoría...</option>
                        {categories.map(c => (
                          <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                      </select>
                    </div>

                  </div>

                  {/* Accompanying info & raw text */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                      <div style={{ display: 'flex', gap: '16px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        {txn.account_name && <span>Detectado: <b>{txn.account_name}</b></span>}
                        {txn.category_name && <span>Categoría original: <b>{txn.category_name}</b></span>}
                      </div>
                      
                      {txn.raw_text && (
                        <button 
                          onClick={() => setExpandedCardId(expandedCardId === txn.id ? null : txn.id)}
                          style={{ background: 'transparent', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}
                        >
                          {expandedCardId === txn.id ? (
                            <>Ocultar texto OCR <ChevronUp size={16} /></>
                          ) : (
                            <>Ver texto OCR <ChevronDown size={16} /></>
                          )}
                        </button>
                      )}
                    </div>

                    {expandedCardId === txn.id && txn.raw_text && (
                      <pre style={{ 
                        margin: '8px 0 0 0', 
                        padding: '12px', 
                        background: 'rgba(0,0,0,0.2)', 
                        borderRadius: '8px', 
                        fontSize: '0.8rem', 
                        color: 'rgba(255,255,255,0.7)',
                        whiteSpace: 'pre-wrap',
                        maxHeight: '150px',
                        overflowY: 'auto',
                        border: '1px solid rgba(255,255,255,0.05)'
                      }}>
                        {txn.raw_text}
                      </pre>
                    )}
                  </div>

                  {/* Actions */}
                  <div style={{ display: 'flex', gap: '12px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '16px' }}>
                    <button 
                      onClick={() => handleConfirm(txn)} 
                      disabled={actioningId !== null}
                      className="glass-button primary" 
                      style={{ flex: 1, display: 'flex', justifyContent: 'center', gap: '8px', padding: '12px' }}
                    >
                      {actioningId === txn.id ? <Loader2 className="spin" size={18} /> : <Check size={18} />}
                      Confirmar y Registrar
                    </button>
                    <button 
                      onClick={() => handleDiscard(txn.id)} 
                      disabled={actioningId !== null}
                      className="glass-button" 
                      style={{ flex: 1, display: 'flex', justifyContent: 'center', gap: '8px', padding: '12px', color: 'var(--color-danger)', borderColor: 'rgba(255,71,87,0.3)' }}
                    >
                      {actioningId === txn.id ? <Loader2 className="spin" size={18} /> : <X size={18} />}
                      Descartar Borrador
                    </button>
                  </div>

                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
