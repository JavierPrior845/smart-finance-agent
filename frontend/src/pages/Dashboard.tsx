import { ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function Dashboard() {
  const data = [
    { name: 'Vivienda', value: 850, color: '#8a2be2' },
    { name: 'Alimentación', value: 420, color: '#00f5d4' },
    { name: 'Ocio', value: 200, color: '#ff007f' },
    { name: 'Transporte', value: 150, color: '#ffbe0b' },
  ];

  return (
    <div className="view-container">
      <div className="view-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Visión general de tus finanzas</p>
        </div>
        <button className="glass-button primary">
          + Nuevo Gasto
        </button>
      </div>

      <div className="kpi-grid">
        <div className="glass-panel kpi-card">
          <span className="kpi-title">Patrimonio Total</span>
          <span className="kpi-value">€12,450.00</span>
          <div className="kpi-trend positive">
            <ArrowUpRight size={16} />
            <span>+2.4% este mes</span>
          </div>
        </div>
        <div className="glass-panel kpi-card">
          <span className="kpi-title">Ingresos Mensuales</span>
          <span className="kpi-value">€3,200.00</span>
          <div className="kpi-trend positive">
            <ArrowUpRight size={16} />
            <span>+0.0% vs pasado</span>
          </div>
        </div>
        <div className="glass-panel kpi-card">
          <span className="kpi-title">Gastos Mensuales</span>
          <span className="kpi-value">€1,620.00</span>
          <div className="kpi-trend negative">
            <ArrowDownRight size={16} />
            <span>+12.4% vs pasado</span>
          </div>
        </div>
        <div className="glass-panel kpi-card">
          <span className="kpi-title">Tasa de Ahorro</span>
          <span className="kpi-value">49.3%</span>
          <div className="kpi-trend">
            <Activity size={16} />
            <span>Objetivo: 50%</span>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '24px', flex: 1, minHeight: '300px' }}>
        <h3 style={{ marginBottom: '16px', color: 'var(--text-secondary)' }}>Distribución de Gastos</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={80}
              outerRadius={110}
              paddingAngle={5}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border-glass)', borderRadius: '8px' }}
              itemStyle={{ color: '#fff' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
