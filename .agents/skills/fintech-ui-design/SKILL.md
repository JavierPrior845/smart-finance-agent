---
name: fintech-ui-design
description: Complete guidelines, design system, and component patterns for creating an impeccable, modern, responsive, and minimal financial dashboard UI. Use this skill whenever designing, building, or modifying frontend interfaces, layouts, CSS styles, or UI components.
---

# Skill: Fintech UI/UX Design System (`fintech-ui-design`)

This skill provides strict, high-fidelity standards and actionable guidelines for building a modern, minimal, highly functional, and visually stunning web interface for **GestorFinanzas**.

The goal is to deliver an interface that feels like a premium SaaS application (inspired by Linear, Wise, Revolut, and Stripe) — clean, uncluttered, intuitive, responsive, and a pleasure to use daily.

---

## 🎨 Design Philosophy & Principles

1. **Minimalist Clarity Over Clutter**:
   - Keep negative space generous (16px–32px padding).
   - High visual hierarchy: key numbers (Balance, Net Worth, Monthly Expenses) must be immediately scannable.
   - Avoid unnecessary borders or heavy dividers; use subtle background tinting (`hsl(220, 15%, 96%)` light / `hsl(222, 47%, 11%)` dark) and soft shadows.

2. **Fintech Color Psychology**:
   - **Neutral Base**: Slate / Charcoal scale (avoid pure `#000` or `#fff` contrast strain).
   - **Primary Brand Accent**: Electric Indigo (`hsl(245, 82%, 67%)`) for primary actions, active tabs, and focused elements.
   - **Income / Profit / Savings**: Emerald Green (`hsl(158, 64%, 52%)`) for positive numbers, inflows, and goal milestones.
   - **Expenses / Outflows**: Crimson Rose (`hsl(350, 78%, 60%)`) for expenses, negative cashflows, and budget warnings.
   - **Info / Category Tags**: Muted Blue, Amber, Purlpe, and Teal for category categorization tags.

3. **Responsive Grid & Mobile-First Layout**:
   - **Desktop (>= 1024px)**: Left collapsible sidebar navigation + sticky topbar + 12-column grid dashboard content.
   - **Tablet (768px - 1023px)**: 2-column or 1-column grid layout with condensed metric cards.
   - **Mobile (< 768px)**: Bottom bar navigation (or hamburger menu), full-width card stack, touch-optimized button hit areas (min 44px height).

4. **Fluid Micro-Interactions & Feedback**:
   - Smooth hover transitions (`150ms - 250ms` ease-out cubic-bezier).
   - Interactive feedback on button presses (`transform: scale(0.98)`).
   - Skeleton screens for loading data instead of blank screens or spinner overlays.
   - Toast notifications for async actions ("Gasto registrado con éxito", "Categoría actualizada").

---

## 📁 Skill Architecture & Reference Documents

When applying this skill, consult the detailed reference guides in the `references/` directory:

- 📄 **[Design Tokens & CSS System](file:///home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/.agents/skills/fintech-ui-design/references/design-tokens.md)**: Color scales (HSL), CSS custom variables, typography scale, elevation shadows, border-radius constants, and transition timings.
- 📄 **[Component Patterns & Layouts](file:///home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/.agents/skills/fintech-ui-design/references/component-patterns.md)**: Concrete HTML/CSS/JS structural patterns for Balance Summary Cards, KPI Grid, Charts, Transaction Tables, Filters, Modals, and Empty States.

---

## 🛠️ Step-by-Step Implementation Workflow

Whenever creating or updating UI elements:

### Step 1: Enforce Core CSS Tokens & Variables
Ensure all colors, font sizes, margins, paddings, and border radii use the predefined CSS variables defined in [design-tokens.md](file:///home/usuario/Documentos/projects/GestorFinanzas/smart-finance-agent/.agents/skills/fintech-ui-design/references/design-tokens.md).
- Never hardcode arbitrary hex colors like `#f00` or `#00f`.
- Use `var(--color-emerald-500)` for income, `var(--color-rose-500)` for expenses, and `var(--bg-surface)` for card containers.

### Step 2: Build Layout Shell & Responsive Navigation
- Set up a clean outer wrapper with CSS Grid or Flexbox.
- Desktop layout: Sidebar fixed at `260px` width, main area filling remaining space with `max-width: 1400px` centered.
- Mobile layout: Fixed bottom bar with icons for "Inicio", "Transacciones", "Presupuestos", "IA Asesor".

### Step 3: Implement Dashboard Hierarchy
Organize the main view into 4 main visual sections:
1. **Header Hero**: Welcome message, current active month/period selector, and primary call-to-action button (`+ Añadir Transacción`).
2. **KPI Metric Row (Cards)**:
   - Total Balance (Large Hero number e.g., `3.450,80 €`).
   - Monthly Income vs Expense comparison.
   - Savings Rate progress indicator (e.g. `24% ahorrado este mes`).
3. **Analytics & Charts Section**:
   - Area chart showing income vs expense trend over time.
   - Donut or horizontal bar chart showing category distribution (Comida, Vivienda, Ocio, etc.).
4. **Recent Transactions Feed**:
   - Search bar + quick category filter chips ("Todos", "Gastos", "Ingresos", "Recurrentes").
   - Transaction list/table with category icon badge, vendor name, category tag, date, and formatted amount.

### Step 4: Add Micro-Interactions & Interactive Polish
- Add `:hover` scale/elevation shifts to cards (`transform: translateY(-2px); box-shadow: var(--shadow-md)`).
- Ensure form inputs have clear `:focus-visible` outline using `var(--color-primary-500)`.
- Format all numeric values with consistent locale formatting (e.g., `Intl.NumberFormat('es-ES', { style: 'currency', currency: 'EUR' })`).

### Step 5: Verification & Quality Assurance
Check list before finalizing any frontend component:
- [ ] Is it responsive across 360px (mobile), 768px (tablet), and 1440px (desktop)?
- [ ] Do all colors have sufficient contrast ratio (WCAG AA standard)?
- [ ] Are hover, active, disabled, and focus states implemented for all interactive elements?
- [ ] Is there an empty state if no transactions exist yet?
- [ ] Are currency values aligned right in tables for easy comparison?
