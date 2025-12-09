import React, { useState } from 'react';
import './Login.css';
import { TrendingUp, Shield, Zap } from 'lucide-react';

const Login = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Limpa erro do campo quando usuario digita
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!isLogin && !formData.name) {
      newErrors.name = 'Nome é obrigatório';
    }

    if (!formData.email) {
      newErrors.email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email inválido';
    }

    if (!formData.password) {
      newErrors.password = 'Senha é obrigatória';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Senha deve ter pelo menos 6 caracteres';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Simula autenticação (em produção, fazer chamada à API)
      const userData = {
        name: formData.name || formData.email.split('@')[0],
        email: formData.email,
        loggedIn: true
      };
      
      // Salva no localStorage
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Chama callback de login
      onLogin(userData);
    }
  };

  const handleDemoLogin = () => {
    const demoUser = {
      name: 'Demo User',
      email: 'demo@arbitrage.com',
      loggedIn: true
    };
    localStorage.setItem('user', JSON.stringify(demoUser));
    onLogin(demoUser);
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      <div className="login-content">
        {/* Hero Section */}
        <div className="login-hero">
          <div className="logo-section">
            <TrendingUp size={48} className="logo-icon" />
            <h1 className="logo-text">Prediction Arbitrage</h1>
          </div>
          
          <p className="hero-subtitle">
            Encontre oportunidades de arbitragem em mercados de predição em tempo real
          </p>

          <div className="features-grid">
            <div className="feature-card">
              <TrendingUp size={24} />
              <h3>24 Oportunidades</h3>
              <p>Mercados ativos</p>
            </div>
            <div className="feature-card">
              <Zap size={24} />
              <h3>Tempo Real</h3>
              <p>Atualizações instantâneas</p>
            </div>
            <div className="feature-card">
              <Shield size={24} />
              <h3>8 Validações</h3>
              <p>Filtros inteligentes</p>
            </div>
          </div>
        </div>

        {/* Form Section */}
        <div className="login-form-container">
          <div className="form-card">
            <div className="form-header">
              <h2>{isLogin ? 'Bem-vindo de volta' : 'Criar conta'}</h2>
              <p>{isLogin ? 'Entre para acessar o dashboard' : 'Comece a encontrar oportunidades'}</p>
            </div>

            <form onSubmit={handleSubmit} className="login-form">
              {!isLogin && (
                <div className="form-group">
                  <label htmlFor="name">Nome completo</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    className={errors.name ? 'error' : ''}
                    placeholder="Seu nome"
                  />
                  {errors.name && <span className="error-message">{errors.name}</span>}
                </div>
              )}

              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={errors.email ? 'error' : ''}
                  placeholder="seu@email.com"
                />
                {errors.email && <span className="error-message">{errors.email}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="password">Senha</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={errors.password ? 'error' : ''}
                  placeholder="••••••••"
                />
                {errors.password && <span className="error-message">{errors.password}</span>}
              </div>

              <button type="submit" className="btn-primary">
                {isLogin ? 'Entrar' : 'Criar conta'}
              </button>

              <button type="button" onClick={handleDemoLogin} className="btn-demo">
                Testar com conta demo
              </button>
            </form>

            <div className="form-footer">
              <p>
                {isLogin ? 'Não tem uma conta?' : 'Já tem uma conta?'}
                {' '}
                <button 
                  className="link-button" 
                  onClick={() => setIsLogin(!isLogin)}
                >
                  {isLogin ? 'Criar conta' : 'Entrar'}
                </button>
              </p>
            </div>
          </div>

          <div className="trust-badges">
            <div className="badge">
              <Shield size={16} />
              <span>Dados seguros</span>
            </div>
            <div className="badge">
              <Zap size={16} />
              <span>Acesso instantâneo</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;

