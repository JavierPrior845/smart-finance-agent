import { Plus } from 'lucide-react';
import './Pages.css';

export default function Budgets() {
  const budgets = [
    { id: 1, category: 'Alimentación', limit: 500, spent: 420, color: 'var(--color-primary)' },
    { id: 2, category: 'Ocio', limit: 200, spent: 250, color: 'var(--color-danger)' },
    { id: 3, category: 'Transporte', limit: 150, spent: 90, color: 'var(--color-secondary)' },
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Presupuestos</h1>
          <p className="page-subtitle">Control de límites por categoría</p>
        </div>
        <button className="glass-button">
          <Plus size={18} />
          Nuevo Presupuesto
        </button>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div className="budget-list">
          {budgets.map(budget => {
            const percent = Math.min((budget.spent / budget.limit) * 100, 100);
            const isOver = budget.spent > budget.limit;
            
            return (
              <div key={budget.id} className="budget-item">
                <div className="budget-info">
                  <h4>{budget.category}</h4>
                  <span>€{budget.spent} / €{budget.limit}</span>
                </div>
                <div className="progress-bg">
                  <div 
                    className="progress-fill" 
                    style={{ 
                      width: `${percent}%`, 
                      background: isOver ? 'var(--color-danger)' : budget.color 
                    }}
                  />
                </div>
                {isOver && <span className="budget-alert">¡Límite excedido!</span>}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
