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

// Interceptor to automatically attach Bearer token to all requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('smartfinance_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor for global error and 401 (token expiration) handling
api.interceptors.response.use(
  (response) => {
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
    const status = error.response?.status;
    const url = error.config?.url || '';

    // Handle token expiration or unauthorized access (except on login/register endpoints)
    if (status === 401 && !url.includes('/auth/login') && !url.includes('/auth/register')) {
      const hadToken = !!localStorage.getItem('smartfinance_token');
      localStorage.removeItem('smartfinance_token');
      localStorage.removeItem('smartfinance_user');
      
      // Dispatch custom event to notify React AuthContext to update state
      window.dispatchEvent(new Event('smartfinance:auth_expired'));

      if (hadToken) {
        toast.error('Tu sesión ha expirado tras 1 hora. Por favor, inicia sesión de nuevo.', {
          id: 'session-expired',
          duration: 4000,
          style: {
            background: 'var(--bg-panel)',
            color: 'var(--text-primary)',
            border: '1px solid var(--color-danger)',
            backdropFilter: 'blur(16px)',
          },
        });
      }
      return Promise.reject(error);
    }

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
