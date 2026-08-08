# Design Tokens & CSS Variables Reference

This document defines the core tokens for the **GestorFinanzas** design system. Use these variables in `index.css` or component styles to ensure visual consistency across the entire application.

---

## 🎨 Color Palette Tokens

```css
:root {
  /* ==========================================================================
     Color Palette (Tailored HSL Scale for Fintech Apps)
     ========================================================================== */
  
  /* Primary Brand Accent (Indigo / Violet) */
  --primary-50:  hsl(245, 100%, 97%);
  --primary-100: hsl(245, 90%, 93%);
  --primary-500: hsl(245, 82%, 67%); /* Main Action & Active Accent */
  --primary-600: hsl(245, 75%, 58%);
  --primary-700: hsl(245, 68%, 48%);
  
  /* Income / Profit / Positive Trend (Emerald Green) */
  --emerald-50:  hsl(152, 81%, 96%);
  --emerald-100: hsl(149, 80%, 90%);
  --emerald-500: hsl(158, 64%, 52%); /* Positive Cashflow / Income */
  --emerald-600: hsl(160, 84%, 39%);
  --emerald-700: hsl(161, 94%, 30%);

  /* Expense / Outflow / Warning (Crimson Rose) */
  --rose-50:  hsl(355, 100%, 97%);
  --rose-100: hsl(355, 95%, 93%);
  --rose-500: hsl(350, 78%, 60%); /* Negative Cashflow / Expenses */
  --rose-600: hsl(348, 83%, 47%);
  --rose-700: hsl(346, 84%, 38%);

  /* Secondary Category Accents */
  --amber-500:  hsl(38, 92%, 50%);  /* Budget Warnings & Savings Goals */
  --sky-500:    hsl(199, 89%, 48%);  /* Subscriptions & Transfers */
  --purple-500: hsl(271, 76%, 53%);  /* Investment & Investments */

  /* Neutral Slate (Light Theme Base) */
  --slate-50:  hsl(210, 40%, 98%);  /* Main App Background */
  --slate-100: hsl(214, 32%, 94%);  /* Card Surfaces & Hover BGs */
  --slate-200: hsl(213, 27%, 84%);  /* Borders & Dividers */
  --slate-400: hsl(215, 16%, 57%);  /* Secondary Text & Muted Icons */
  --slate-700: hsl(215, 25%, 27%);  /* Body Text */
  --slate-900: hsl(222, 47%, 11%);  /* Primary Headings & Bold Text */

  /* Dark Theme Surfaces (Sleek Dark Mode Slate) */
  --dark-bg:      hsl(224, 25%, 8%);   /* Deep Midnight Background */
  --dark-surface: hsl(222, 20%, 12%);  /* Elevated Card Surface */
  --dark-surface-hover: hsl(220, 18%, 16%);
  --dark-border:  hsl(220, 16%, 18%);  /* Subdued Dark Border */
  --dark-text-main: hsl(210, 20%, 96%);
  --dark-text-muted: hsl(217, 12%, 63%);

  /* Semantic Variables (Light Mode Default) */
  --bg-app: var(--slate-50);
  --bg-surface: #ffffff;
  --bg-surface-hover: var(--slate-100);
  --border-color: var(--slate-200);
  --text-main: var(--slate-900);
  --text-muted: var(--slate-400);

  /* ==========================================================================
     Typography & Font Hierarchy
     ========================================================================== */
  --font-family-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-family-mono: 'JetBrains Mono', 'Fira Code', monospace; /* For numbers/amounts */

  --text-xs:   0.75rem;   /* 12px - Badges, Small Metadata */
  --text-sm:   0.875rem;  /* 14px - Table Rows, Secondary Text */
  --text-base: 1rem;      /* 16px - Body Text, Standard Buttons */
  --text-lg:   1.125rem;  /* 18px - Section Subtitles, Card Titles */
  --text-xl:   1.25rem;   /* 20px - Card Hero Subtext */
  --text-2xl:  1.5rem;    /* 24px - Section Titles */
  --text-3xl:  1.875rem;  /* 30px - KPI Metric Highlights */
  --text-4xl:  2.25rem;   /* 36px - Total Net Worth Hero */

  /* ==========================================================================
     Spacing & Layout Scale
     ========================================================================== */
  --space-1: 0.25rem; /* 4px */
  --space-2: 0.5rem;  /* 8px */
  --space-3: 0.75rem; /* 12px */
  --space-4: 1rem;    /* 16px */
  --space-6: 1.5rem;  /* 24px */
  --space-8: 2rem;    /* 32px */
  --space-12: 3rem;   /* 48px */

  /* ==========================================================================
     Border Radius (Rounded Minimalist Look)
     ========================================================================== */
  --radius-sm: 6px;   /* Buttons, Input Fields, Badges */
  --radius-md: 10px;  /* Cards, Dropdowns */
  --radius-lg: 16px;  /* Main Dashboard Containers, Modals */
  --radius-full: 9999px; /* Pill Filter Chips, Avatars */

  /* ==========================================================================
     Shadows & Elevations (Glassmorphism & Depth)
     ========================================================================== */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-glow: 0 0 16px rgba(99, 102, 241, 0.25); /* Subtle glow for active items */

  /* ==========================================================================
     Animations & Transitions
     ========================================================================== */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-bounce: 350ms cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* ==========================================================================
   Dark Theme Auto Overlay Overrides
   ========================================================================== */
[data-theme="dark"] {
  --bg-app: var(--dark-bg);
  --bg-surface: var(--dark-surface);
  --bg-surface-hover: var(--dark-surface-hover);
  --border-color: var(--dark-border);
  --text-main: var(--dark-text-main);
  --text-muted: var(--dark-text-muted);
}
```
