import { useState, useEffect } from 'react';
import { X, Loader2, ArrowUpRight, ArrowDownLeft, ArrowRightLeft, Calendar } from 'lucide-react';
import api from '../services/api';

interface Transaction {
  id: string;
  amount: number;
  description: string;
  type: 'EXPENSE' | 'INCOME' | 'TRANSFER' | 'BALANCE_ADJUSTMENT' | 'INVESTMENT_OUTFLOW' | 'INVESTMENT_INFLOW';
  transaction_date: string;
  source: string;
  currency: string;
  account_id: string;
}

interface CategoryTransactionsModalProps {
  categoryId: string;
  categoryName: string;
  categoryColor?: string;
  categoryType?: string;
  month: number;
  year: number;
  onClose: () => void;
}

const MONTH_NAMES = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

export default function CategoryTransactionsModal({
  categoryId,
  categoryName,
  categoryColor = 'var(--color-primary)',
  categoryType,
  month,
  year,
  onClose
}: CategoryTransactionsModalProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCategoryTransactions = async () => {
      try {
        setLoading(true);
        const res = await api.get('/transactions', {
          params: {
            category_id: categoryId,
            month: month,
            year: year,
            limit: 50
          }
        });
        setTransactions(res.data.items || []);
        setTotalCount(res.data.total || 0);
      } catch (err) {
        console.error('Error al cargar movimientos de la categoría:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryTransactions();
  }, [categoryId, month, year]);

  // Totales calculados
  const totalExpenses = transactions
    .filter(t => t.type === 'EXPENSE' || t.type === 'INVESTMENT_OUTFLOW')
    .reduce((acc, t) => acc + Math.abs(t.amount), 0);

  const totalIncomes = transactions
    .filter(t => t.type === 'INCOME' || t.type === 'INVESTMENT_INFLOW')
    .reduce((acc, t) => acc + Math.abs(t.amount), 0);

  const isInvestmentCat = categoryType === 'INVESTMENT';
  const netBalance = totalExpenses - totalIncomes;

  return (
    <div 
      className="modal-overlay" 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(5, 5, 10, 0.75)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
        padding: '20px'
      }}
      onClick={onClose}
    >
      <div 
        className="glass-panel" 
        style={{
          width: '100%',
          maxWidth: '720px',
          maxHeight: '90vh',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          animation: 'fadeIn 0.2s ease-out'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header del Modal */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.02)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '14px',
              height: '14px',
              borderRadius: '50%',
              backgroundColor: categoryColor,
              boxShadow: `0 0 10px ${categoryColor}`
            }} />
            <div>
              <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {categoryName}
              </h2>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px', fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                <Calendar size={14} />
                <span>{MONTH_NAMES[month - 1]} {year}</span>
                <span style={{ opacity: 0.4 }}>•</span>
                <span>{totalCount} movimiento{totalCount !== 1 ? 's' : ''}</span>
              </div>
            </div>
          </div>

          <button 
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              padding: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s ease'
            }}
            title="Cerrar"
          >
            <X size={20} />
          </button>
        </div>

        {/* Resumen de Flujos Netos */}
        {!loading && transactions.length > 0 && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr 1fr',
            gap: '12px',
            padding: '16px 24px',
            background: 'rgba(0, 0, 0, 0.2)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.05)'
          }}>
            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.04)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
                {isInvestmentCat ? 'Aportes / Compras' : 'Gastos Totales'}
              </span>
              <span style={{ fontSize: '1.05rem', fontWeight: 600, color: isInvestmentCat ? '#a855f7' : 'var(--color-danger)' }}>
                €{totalExpenses.toFixed(2)}
              </span>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.04)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
                {isInvestmentCat ? 'Ventas / Reembolsos' : 'Abonos / Reembolsos'}
              </span>
              <span style={{ fontSize: '1.05rem', fontWeight: 600, color: 'var(--color-success)' }}>
                €{totalIncomes.toFixed(2)}
              </span>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.03)', padding: '10px 14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.04)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>Flujo Neto</span>
              <span style={{ 
                fontSize: '1.05rem', 
                fontWeight: 600, 
                color: isInvestmentCat ? '#a855f7' : netBalance >= 0 ? '#60a5fa' : 'var(--color-success)' 
              }}>
                €{netBalance.toFixed(2)}
              </span>
            </div>
          </div>
        )}

        {/* Contenido / Listado de Transacciones */}
        <div style={{
          padding: '20px 24px',
          overflowY: 'auto',
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: '10px'
        }}>
          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '50px 0' }}>
              <Loader2 className="spin" size={32} style={{ color: 'var(--color-primary-light)', marginBottom: '12px' }} />
              <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Cargando movimientos...</span>
            </div>
          ) : transactions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
              <p style={{ margin: 0, fontSize: '0.95rem' }}>No hay transacciones registradas en esta categoría para este mes.</p>
            </div>
          ) : (
            transactions.map((tx) => {
              const isOutflow = tx.type === 'EXPENSE' || tx.type === 'INVESTMENT_OUTFLOW';
              const isInflow = tx.type === 'INCOME' || tx.type === 'INVESTMENT_INFLOW';
              const isInvestmentTx = tx.type === 'INVESTMENT_OUTFLOW' || tx.type === 'INVESTMENT_INFLOW';
              const formattedDate = new Date(tx.transaction_date).toLocaleDateString('es-ES', {
                day: '2-digit',
                month: 'short',
                year: 'numeric'
              });

              return (
                <div 
                  key={tx.id} 
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '12px 16px',
                    borderRadius: '12px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.05)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '10px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: isInvestmentTx
                        ? 'rgba(168, 85, 247, 0.15)'
                        : isOutflow
                        ? 'rgba(255, 51, 102, 0.12)'
                        : isInflow
                        ? 'rgba(0, 255, 127, 0.12)'
                        : 'rgba(59, 130, 246, 0.12)',
                      color: isInvestmentTx
                        ? '#c084fc'
                        : isOutflow
                        ? 'var(--color-danger)'
                        : isInflow
                        ? 'var(--color-success)'
                        : '#60a5fa'
                    }}>
                      {isOutflow && <ArrowUpRight size={18} />}
                      {isInflow && <ArrowDownLeft size={18} />}
                      {!isOutflow && !isInflow && <ArrowRightLeft size={18} />}
                    </div>

                    <div>
                      <div style={{ fontWeight: 500, color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                        {tx.description || 'Sin descripción'}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                        {formattedDate} • <span style={{ textTransform: 'capitalize' }}>{tx.source}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{
                    fontWeight: 600,
                    fontSize: '1rem',
                    color: isInvestmentTx
                      ? '#c084fc'
                      : isOutflow
                      ? 'var(--color-danger)'
                      : isInflow
                      ? 'var(--color-success)'
                      : 'var(--text-primary)'
                  }}>
                    {isOutflow ? '-' : isInflow ? '+' : ''}€{Math.abs(tx.amount).toFixed(2)}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          display: 'flex',
          justifyContent: 'flex-end',
          background: 'rgba(0, 0, 0, 0.2)'
        }}>
          <button 
            className="glass-button" 
            onClick={onClose}
            style={{ fontSize: '0.9rem', padding: '6px 18px' }}
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
