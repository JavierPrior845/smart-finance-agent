import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  created_at?: string;
  last_login_at?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('smartfinance_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('smartfinance_token');
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Validate token on mount
  useEffect(() => {
    const verifySession = async () => {
      const storedToken = localStorage.getItem('smartfinance_token');
      if (!storedToken) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
        localStorage.setItem('smartfinance_user', JSON.stringify(response.data));
      } catch (err) {
        // Token invalid or expired
        localStorage.removeItem('smartfinance_token');
        localStorage.removeItem('smartfinance_user');
        setUser(null);
        setToken(null);
      } finally {
        setIsLoading(false);
      }
    };

    verifySession();

    // Listen for global expiration events dispatched by api interceptor
    const handleAuthExpired = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('smartfinance:auth_expired', handleAuthExpired);
    return () => {
      window.removeEventListener('smartfinance:auth_expired', handleAuthExpired);
    };
  }, []);

  const login = async (email: string, password: string) => {
    const response = await api.post('/auth/login', { email, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('smartfinance_token', access_token);
    localStorage.setItem('smartfinance_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);
  };

  const register = async (name: string, email: string, password: string) => {
    const response = await api.post('/auth/register', { name, email, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('smartfinance_token', access_token);
    localStorage.setItem('smartfinance_user', JSON.stringify(userData));

    setToken(access_token);
    setUser(userData);
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      // Ignore logout errors if token already invalidated
    } finally {
      localStorage.removeItem('smartfinance_token');
      localStorage.removeItem('smartfinance_user');
      setUser(null);
      setToken(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
