import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './components/Login';
import DashboardModern from './components/DashboardModern';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Verifica se usuario ja esta logado ao carregar
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        if (userData.loggedIn) {
          setUser(userData);
        }
      } catch (error) {
        console.error('Erro ao carregar usuario salvo:', error);
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  // Mostra loading enquanto verifica autenticacao
  if (loading) {
    return (
      <div className="app-loading">
        <div className="spinner"></div>
        <p>Carregando...</p>
      </div>
    );
  }

  // Mostra login se nao estiver autenticado
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  // Mostra dashboard se estiver autenticado
  return <DashboardModern user={user} onLogout={handleLogout} />;
}

export default App;
