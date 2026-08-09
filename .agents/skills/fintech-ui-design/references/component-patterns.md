# Fintech Component Patterns & Layout Specifications

This document defines reusable, clean HTML/CSS structural patterns for building **GestorFinanzas** UI components.

---

## 1. App Shell & Responsive Grid Layout

The layout uses a two-column grid on desktop (Sidebar + Main Content) and a single-column layout with bottom navigation on mobile devices.

```html
<!-- App Container Shell -->
<div class="app-layout">
  <!-- Desktop Sidebar Navigation -->
  <aside class="app-sidebar">
    <div class="brand-logo">
      <svg class="logo-icon"><!-- Financial Pulse Icon --></svg>
      <span class="logo-text">GestorFinanzas</span>
    </div>

    <nav class="nav-menu">
      <a href="#dashboard" class="nav-item active">
        <span class="nav-icon">📊</span>
        <span>Panel Principal</span>
      </a>
      <a href="#transactions" class="nav-item">
        <span class="nav-icon">💳</span>
        <span>Transacciones</span>
      </a>
      <a href="#budgets" class="nav-item">
        <span class="nav-icon">🎯</span>
        <span>Presupuestos</span>
      </a>
      <a href="#ai-advisor" class="nav-item">
        <span class="nav-icon">🤖</span>
        <span>Asesor IA</span>
      </a>
    </nav>
  </aside>

  <!-- Main Content Area -->
  <main class="app-main">
    <header class="topbar">
      <div class="header-title">
        <h1>¡Hola, David! 👋</h1>
        <p class="subtitle">Aquí tienes el resumen de tus finanzas este mes.</p>
      </div>

      <div class="header-actions">
        <!-- Date Period Picker -->
        <select class="period-select">
          <option value="current">Agosto 2026</option>
          <option value="last">Julio 2026</option>
        </select>
        <!-- Primary Add Action -->
        <button class="btn btn-primary" id="btn-open-add-modal">
          <span class="btn-icon">+</span>
          <span>Añadir Transacción</span>
        </button>
      </div>
    </header>

    <section class="dashboard-grid">
      <!-- KPI Cards & Charts go here -->
    </section>
  </main>
</div>
```

```css
/* Layout CSS Grid */
.app-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
  background-color: var(--bg-app);
}

@media (max-width: 1024px) {
  .app-layout {
    grid-template-columns: 1fr;
  }
  .app-sidebar {
    display: none; /* Replaced by bottom nav on mobile */
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--space-6);
  padding: var(--space-6);
}
```

---

## 2. Balance Hero & KPI Metric Cards

Key metrics must be immediately readable using clear typography and visual color coding.

```html
<!-- KPI Cards Row (Span 12 Columns in Grid) -->
<div class="kpi-card kpi-balance col-span-4">
  <div class="kpi-header">
    <span class="kpi-title">Balance Total</span>
    <span class="kpi-badge badge-neutral">Actualizado hoy</span>
  </div>
  <div class="kpi-value text-hero">3.450,80 €</div>
  <div class="kpi-footer text-emerald">
    <span>↑ +12,4% vs mes anterior</span>
  </div>
</div>

<div class="kpi-card kpi-income col-span-4">
  <div class="kpi-header">
    <span class="kpi-title">Ingresos Totales</span>
    <span class="icon-circle bg-emerald-soft">↓</span>
  </div>
  <div class="kpi-value text-emerald">2.850,00 €</div>
  <div class="kpi-footer text-muted">2 fuentes registradas</div>
</div>

<div class="kpi-card kpi-expense col-span-4">
  <div class="kpi-header">
    <span class="kpi-title">Gastos Totales</span>
    <span class="icon-circle bg-rose-soft">↑</span>
  </div>
  <div class="kpi-value text-rose">1.399,20 €</div>
  <div class="kpi-footer">
    <!-- Progress bar for budget -->
    <div class="progress-bar-container">
      <div class="progress-bar-fill bg-amber" style="width: 70%;"></div>
    </div>
    <span class="text-xs text-muted">70% del presupuesto gastado</span>
  </div>
</div>
```

```css
.kpi-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.text-hero {
  font-size: var(--text-4xl);
  font-weight: 700;
  font-family: var(--font-family-mono);
  color: var(--text-main);
  letter-spacing: -0.02em;
  margin: var(--space-2) 0;
}

.text-emerald { color: var(--emerald-500); }
.text-rose { color: var(--rose-500); }
```

---

## 3. Transaction Feed & Interactive Table

The transaction feed includes quick filtering chips, a search input, and a clean tabular view.

```html
<div class="card col-span-12">
  <div class="card-header">
    <h3>Últimas Transacciones</h3>

    <!-- Quick Filter Chips -->
    <div class="filter-group">
      <input type="text" class="input-search" placeholder="Buscar concepto..." />
      <button class="chip active">Todas</button>
      <button class="chip">Gastos</button>
      <button class="chip">Ingresos</button>
    </div>
  </div>

  <div class="table-responsive">
    <table class="transaction-table">
      <thead>
        <tr>
          <th>Concepto</th>
          <th>Categoría</th>
          <th>Fecha</th>
          <th>Método</th>
          <th class="text-right">Monto</th>
        </tr>
      </thead>
      <tbody>
        <!-- Transaction Row -->
        <tr class="transaction-row">
          <td>
            <div class="vendor-cell">
              <div class="category-icon bg-blue-soft">🛒</div>
              <div>
                <div class="vendor-name">Mercadona</div>
                <div class="text-xs text-muted">Compra semanal</div>
              </div>
            </div>
          </td>
          <td><span class="badge badge-category">Supermercado</span></td>
          <td><span class="text-sm">08 Aug 2026</span></td>
          <td><span class="text-sm text-muted">Tarjeta</span></td>
          <td class="text-right font-mono text-rose">-84,50 €</td>
        </tr>

        <!-- Transaction Row Income -->
        <tr class="transaction-row">
          <td>
            <div class="vendor-cell">
              <div class="category-icon bg-emerald-soft">💼</div>
              <div>
                <div class="vendor-name">Nómina Empresa</div>
                <div class="text-xs text-muted">Pago mensual</div>
              </div>
            </div>
          </td>
          <td><span class="badge badge-category">Salario</span></td>
          <td><span class="text-sm">01 Aug 2026</span></td>
          <td><span class="text-sm text-muted">Transferencia</span></td>
          <td class="text-right font-mono text-emerald">+2.500,00 €</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

---

## 4. Modal Dialog Pattern (Adding New Transaction)

Accessible modal dialog pattern with smooth backdrop blur.

```html
<div class="modal-backdrop" id="add-transaction-modal" style="display: none;">
  <div class="modal-card">
    <div class="modal-header">
      <h2>Añadir Nueva Transacción</h2>
      <button class="btn-close" aria-label="Cerrar">&times;</button>
    </div>
    
    <form id="form-add-transaction" class="modal-body">
      <!-- Segmented Control for Type -->
      <div class="segmented-control">
        <button type="button" class="segmented-btn active" data-type="expense">Gasto</button>
        <button type="button" class="segmented-btn" data-type="income">Ingreso</button>
      </div>

      <!-- Large Hero Amount Input -->
      <div class="amount-input-group">
        <span class="currency-symbol">€</span>
        <input type="number" step="0.01" class="input-amount" placeholder="0,00" required autofocus />
      </div>

      <!-- Form Grid -->
      <div class="form-grid">
        <div class="form-field">
          <label>Concepto</label>
          <input type="text" class="input-text" placeholder="Ej: Cena con amigos" required />
        </div>

        <div class="form-field">
          <label>Categoría</label>
          <select class="input-select" required>
            <option value="">Selecciona categoría</option>
            <option value="ocio">🎉 Ocio y Restaurantes</option>
            <option value="supermercado">🛒 Supermercado</option>
            <option value="vivienda">🏠 Vivienda / Alquiler</option>
            <option value="transporte">🚗 Transporte</option>
          </select>
        </div>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary btn-cancel">Cancelar</button>
        <button type="submit" class="btn btn-primary">Guardar Transacción</button>
      </div>
    </form>
  </div>
</div>
```

```css
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn var(--transition-fast);
}

.modal-card {
  background-color: var(--bg-surface);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 500px;
  padding: var(--space-6);
  box-shadow: var(--shadow-lg);
}
```
