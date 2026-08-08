import { FileUp, Key } from 'lucide-react';
import './Pages.css';

export default function Settings() {
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
            <FileUp size={20} /> Importación Manual
          </h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '16px', fontSize: '0.9rem' }}>
            Arrastra aquí tus archivos CSV del banco o facturas en PDF para procesarlos con IA.
          </p>
          <div style={{
            border: '2px dashed var(--border-glass)',
            borderRadius: '12px',
            padding: '40px',
            textAlign: 'center',
            cursor: 'pointer',
            background: 'rgba(255,255,255,0.02)'
          }}>
            <FileUp size={32} style={{ color: 'var(--color-primary)', marginBottom: '12px' }} />
            <p><strong>Haz clic o arrastra un archivo</strong></p>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>CSV, PDF, JPG admitidos</p>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h3>Reglas de Categorización (Comercios)</h3>
          <button className="glass-button">+ Nueva Regla</button>
        </div>
        
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Patrón de Búsqueda (Texto/Regex)</th>
                <th>Categoría a Asignar</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><code>MERCADONA</code></td>
                <td><span className="cat-badge">Alimentación</span></td>
                <td><button className="glass-button" style={{ padding: '4px 8px', fontSize: '0.8rem' }}>Editar</button></td>
              </tr>
              <tr>
                <td><code>NETFLIX</code></td>
                <td><span className="cat-badge">Ocio</span></td>
                <td><button className="glass-button" style={{ padding: '4px 8px', fontSize: '0.8rem' }}>Editar</button></td>
              </tr>
              <tr>
                <td><code>IBERDROLA</code></td>
                <td><span className="cat-badge">Vivienda</span></td>
                <td><button className="glass-button" style={{ padding: '4px 8px', fontSize: '0.8rem' }}>Editar</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
