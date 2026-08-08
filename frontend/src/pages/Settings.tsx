import { useState, useEffect } from 'react';
import { FileUp, Key, Target, Loader2, Save } from 'lucide-react';
import api from '../services/api';
import './Pages.css';

export default function Settings() {
  const [targetSavingsRate, setTargetSavingsRate] = useState<string>("50.0");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await api.get('/settings/target_savings_rate');
        setTargetSavingsRate(res.data.value);
      } catch (err) {
        console.error("No se pudo cargar la tasa de ahorro objetivo", err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, []);

  const handleSaveSavingsRate = async () => {
    setSaving(true);
    try {
      await api.put('/settings/target_savings_rate', {
        value: targetSavingsRate,
        description: "Tasa de ahorro objetivo (%)"
      });
      // Podríamos mostrar un toast de éxito aquí
    } catch (err) {
      console.error("Error al guardar la tasa de ahorro", err);
    } finally {
      setSaving(false);
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
