# 🎨 Smart Finance Agent - Frontend Web Dashboard

Esta aplicación web es el **Dashboard Interactivo** para el Gestor de Finanzas Personal. Está construida usando **React** + **Vite** + **Vanilla CSS** con un diseño *Glassmorphism* (cristal mate) enfocado en máxima estética moderna, fluidez visual y respuesta adaptativa.

---

## 💻 Características del Dashboard

- 📊 **Visualización de Presupuestos:** Tarjetas interactivas con barras de progreso animadas, indicadores de salud financiera y alertas de sobregasto.
- 💸 **Gestión de Transacciones:** Tabla de gastos e ingresos con filtrado por cuenta y categoría, más modal para añadir transacciones manualmente.
- 🏦 **Cuentas & Métricas:** Resumen de balance total en tiempo real y saldos desglosados por cuenta bancaria o efectivo.
- ⚡ **Diseño Ultra-Fluido:** Efectos hover, micro-animaciones, gradientes oscuros elegantes y tipografía moderna Inter/Outfit.

---

## 🚀 Inicio Rápido (Desarrollo Local)

### 1. Instalar dependencias
Asegúrate de tener **Node.js** (v18+) instalado. Desde este directorio (`frontend/`), ejecuta:
```bash
npm install
```

### 2. Levantar el Servidor de Desarrollo
```bash
npm run dev
```
La aplicación se levantará en `http://localhost:5173`. Vite soporta recarga rápida instantánea (HMR).

### 3. Conexión con el Backend (Proxy API)
Por defecto, las peticiones hacia `/api/v1` en desarrollo se redirigen automáticamente al backend local de FastAPI (`http://localhost:8000`) gracias a la configuración en `vite.config.js`.

### 4. Compilación para Producción
Para generar los archivos estáticos listos para ser desplegados en un servidor Nginx o contenedor Docker:
```bash
npm run build
```
Los archivos minificados quedarán generados en la carpeta `dist/`.

---

## 📦 Estructura del Proyecto

```
frontend/src/
├── components/        # Componentes UI reutilizables (Navbar, Cards, Modals)
├── pages/             # Páginas principales (Dashboard, Transactions, Accounts)
├── services/          # Cliente API HTTP (Axios)
├── styles/            # Sistema de diseño CSS global y tokens de color
└── App.jsx            # Enrutador SPA con React Router V6
```
