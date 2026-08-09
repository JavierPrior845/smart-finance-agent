import axios from 'axios';
import toast from 'react-hot-toast';

// Create an Axios instance configured for our FastAPI backend
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor for global error handling
api.interceptors.response.use(
  (response) => {
    // We can also trigger success toasts here if needed based on method
    if (response.config.method !== 'get' && response.status >= 200 && response.status < 300) {
      toast.success('Operación realizada con éxito', {
        style: {
          background: 'var(--bg-panel)',
          color: 'var(--text-primary)',
          border: '1px solid var(--color-success)',
          backdropFilter: 'blur(16px)',
        },
      });
    }
    return response;
  },
  (error) => {
    // Handle error globally
    const message = error.response?.data?.detail || error.message || 'Error de conexión con el servidor';
    
    toast.error(`Error: ${message}`, {
      style: {
        background: 'var(--bg-panel)',
        color: 'var(--text-primary)',
        border: '1px solid var(--color-danger)',
        backdropFilter: 'blur(16px)',
      },
    });
    
    return Promise.reject(error);
  }
);

export default api;
