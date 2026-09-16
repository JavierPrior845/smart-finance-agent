import React, { useState, useEffect } from 'react';
import { Shield, Lock, Mail, User, ArrowRight, Loader2, KeyRound } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './Login.css';

export default function Login() {
  const { login, register } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Check setup status on load
  useEffect(() => {
    const checkSetup = async () => {
      try {
        const res = await api.get('/auth/setup-status');
        setIsConfigured(res.data.is_configured);
        if (!res.data.is_configured) {
          setIsRegisterMode(true);
        }
      } catch {
        setIsConfigured(true);
      }
    };
    checkSetup();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setIsLoading(true);

    try {
      if (isRegisterMode) {
        await register(name, email, password);
      } else {
        await login(email, password);
      }
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Error al autenticar. Verifica tus credenciales.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-page-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-logo-glow">
            <Shield size={28} />
          </div>

          <div className="auth-badge">
            <KeyRound size={13} />
            <span>Self-Hosted Security</span>
          </div>

          <h1>{isRegisterMode ? (isConfigured === false ? 'Configuración Inicial' : 'Crear Usuario') : 'Iniciar Sesión'}</h1>
          <p>
            {isRegisterMode
              ? isConfigured === false
                ? 'Define la cuenta de administrador local para tu instancia'
                : 'Registra una nueva cuenta de acceso a tu gestor'
              : 'Introduce tus credenciales para acceder a tus finanzas'}
          </p>
        </div>

        {errorMessage && (
          <div
            style={{
              background: 'rgba(255, 51, 102, 0.15)',
              border: '1px solid var(--color-danger)',
              color: 'var(--color-danger)',
              padding: '0.75rem 1rem',
              borderRadius: '0.75rem',
              fontSize: '0.85rem',
              marginBottom: '1.25rem',
              textAlign: 'center',
            }}
          >
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          {isRegisterMode && (
            <div className="form-group">
              <label htmlFor="name">Nombre Completo</label>
              <div className="input-wrapper">
                <User size={18} className="input-icon" />
                <input
                  id="name"
                  type="text"
                  placeholder="Tu nombre o Administrador"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </div>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Correo Electrónico</label>
            <div className="input-wrapper">
              <Mail size={18} className="input-icon" />
              <input
                id="email"
                type="email"
                placeholder="admin@smartfinance.local"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña Maestra</label>
            <div className="input-wrapper">
              <Lock size={18} className="input-icon" />
              <input
                id="password"
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
            </div>
          </div>

          <button type="submit" className="btn-submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                <span>Verificando...</span>
              </>
            ) : (
              <>
                <span>{isRegisterMode ? 'Crear Cuenta y Entrar' : 'Acceder'}</span>
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        {isConfigured !== false && (
          <div className="auth-toggle">
            {isRegisterMode ? '¿Ya tienes una cuenta?' : '¿Quieres añadir otro usuario?'}
            <button
              type="button"
              onClick={() => {
                setIsRegisterMode(!isRegisterMode);
                setErrorMessage('');
              }}
            >
              {isRegisterMode ? 'Inicia sesión aquí' : 'Registrar'}
            </button>
          </div>
        )}

        <div className="security-notice">
          <Lock size={13} />
          <span>Sesión Bearer Token cifrada de 1 hora de duración</span>
        </div>
      </div>
    </div>
  );
}
