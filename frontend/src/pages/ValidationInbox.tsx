import { Check, X, Split, MessageSquare } from 'lucide-react';
import './Pages.css';

export default function ValidationInbox() {
  const pendingTransactions = [
    {
      id: 'tx-001',
      date: '2023-11-20',
      desc: 'MERCADONA SUPERM',
      amount: -54.30,
      cat: 'Alimentación',
      source: 'Telegram Voice',
      confidence: 0.92,
      note: 'Compra semanal carne y verduras',
    },
    {
      id: 'tx-002',
      date: '2023-11-21',
      desc: 'AMAZON EU SARL',
      amount: -120.00,
      cat: 'Electrónica',
      source: 'OCR',
      confidence: 0.75,
      note: '',
    }
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Inbox de Validación</h1>
          <p className="page-subtitle">Revisa las operaciones extraídas por IA antes de confirmarlas</p>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        {pendingTransactions.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            <MessageSquare size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
            <h3>Todo al día</h3>
            <p>No tienes transacciones pendientes de revisión.</p>
          </div>
        ) : (
          <div className="account-list">
            {pendingTransactions.map(txn => (
              <div key={txn.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
                  <div>
                    <h3 style={{ marginBottom: '8px', fontSize: '1.2rem' }}>{txn.desc}</h3>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)', flexWrap: 'wrap' }}>
                      <span>{txn.date}</span>
                      <span>•</span>
                      <span className="cat-badge">{txn.cat}</span>
                      <span>•</span>
                      <span>Confianza: {(txn.confidence * 100).toFixed(0)}%</span>
                      <span>•</span>
                      <span>Fuente: {txn.source}</span>
                    </div>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-primary)' }}>
                    €{Math.abs(txn.amount).toFixed(2)}
                  </div>
                </div>
                
                {txn.note && (
                  <div style={{ padding: '12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', fontSize: '0.9rem' }}>
                    <strong>Nota extraída: </strong> {txn.note}
                  </div>
                )}

                <div style={{ display: 'flex', gap: '12px', marginTop: '8px', flexWrap: 'wrap' }}>
                  <button className="glass-button primary" style={{ flex: '1 1 120px', display: 'flex', justifyContent: 'center', gap: '8px' }}>
                    <Check size={18} /> Aprobar
                  </button>
                  <button className="glass-button" style={{ flex: '1 1 120px', display: 'flex', justifyContent: 'center', gap: '8px' }}>
                    <Split size={18} /> Dividir
                  </button>
                  <button className="glass-button" style={{ flex: '1 1 120px', color: 'var(--color-danger)', border: '1px solid rgba(255,71,87,0.3)' }}>
                    <X size={18} /> Descartar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
