# Smart Finance Agent - Frontend Web Dashboard

Esta aplicación web es el Dashboard interactivo para el Gestor de Finanzas. Está construida usando **React** + **Vite** + **Vanilla CSS** con un diseño *Glassmorphism* (cristal mate) muy enfocado en estética moderna y fluidez.

## 🚀 Inicio Rápido (Desarrollo Local)

Para levantar el entorno de desarrollo y hacer cambios en la interfaz web, sigue estos pasos:

### 1. Instalar dependencias
Asegúrate de tener Node.js instalado. Luego, desde esta carpeta (`frontend/`), instala los paquetes necesarios:
```bash
npm install
```

### 2. Levantar el Servidor de Desarrollo
```bash
npm run dev
```
La aplicación se levantará instantáneamente y podrás verla abriendo el enlace en tu navegador (por defecto `http://localhost:5173`). Vite soporta recarga rápida (HMR), por lo que verás tus cambios reflejados de inmediato al guardar.

### 3. Compilación para Producción
Para generar los archivos estáticos listos para ser servidos (por ejemplo, en un contenedor Nginx):
```bash
npm run build
```
Los archivos minificados quedarán en el directorio `dist/`.

## 📦 Dependencias Clave
- **react-router-dom:** Para el enrutamiento tipo Single Page Application (SPA).
- **axios:** Para las futuras conexiones con el Backend de FastAPI.
- **recharts:** Para la visualización de datos (ej. Gráfico circular del Dashboard).
- **lucide-react:** Para la iconografía del sistema.
