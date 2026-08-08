import { Plus, Filter } from 'lucide-react';
import './Pages.css';

export default function Transactions() {
  const transactions = [
    { id: 1, date: '2023-10-25', desc: 'Mercadona', amount: -45.50, cat: 'Alimentación' },
    { id: 2, date: '2023-10-24', desc: 'Nómina', amount: 3200.00, cat: 'Ingresos' },
    { id: 3, date: '2023-10-22', desc: 'Uber', amount: -15.20, cat: 'Transporte' },
    { id: 4, date: '2023-10-21', desc: 'Restaurante El Paso', amount: -60.00, cat: 'Ocio' },
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Histórico de Transacciones</h1>
          <p className="page-subtitle">Registro detallado de movimientos</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <div className="page-controls">
            <button className="glass-button primary">+ Añadir Transacción</button>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '16px 24px', marginBottom: '-16px' }}>
        <div className="filters-bar">
          <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
            <label>Buscar</label>
            <input type="text" placeholder="Concepto, comercio..." />
          </div>
          <div className="input-group" style={{ minWidth: '150px' }}>
            <label>Categoría</label>
            <select>
              <option value="">Todas</option>
              <option value="alimentacion">Alimentación</option>
              <option value="vivienda">Vivienda</option>
              <option value="ocio">Ocio</option>
            </select>
          </div>
          <div className="input-group" style={{ minWidth: '150px' }}>
            <label>Fuente</label>
            <select>
              <option value="">Todas</option>
              <option value="telegram">Telegram</option>
              <option value="csv">Import (CSV)</option>
              <option value="manual">Manual</option>
            </select>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end', alignSelf: 'stretch', paddingBottom: '2px' }}>
            <button className="glass-button primary" style={{ height: '38px', marginTop: 'auto' }}>Aplicar</button>
            <button className="glass-button" style={{ height: '38px', marginTop: 'auto' }}>Limpiar</button>
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
                <th style={{ textAlign: 'right' }}>Importe</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(txn => (
                <tr key={txn.id}>
                  <td style={{ color: 'var(--text-secondary)' }}>{txn.date}</td>
                  <td><strong>{txn.desc}</strong></td>
                  <td><span className="cat-badge">{txn.cat}</span></td>
                  <td style={{ textAlign: 'right' }} className={txn.amount > 0 ? 'text-success' : 'text-primary'}>
                    {txn.amount > 0 ? '+' : ''}€{Math.abs(txn.amount).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        <div className="pagination">
          <span>Mostrando 1-4 de 45</span>
          <div className="page-controls">
            <button className="glass-button">&lt;</button>
            <button className="glass-button">&gt;</button>
          </div>
        </div>
      </div>
    </div>
  );
}
