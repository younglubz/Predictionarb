import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import './theme.css';
import App from './App';
import ErrorBoundary from './ErrorBoundary';

// Aplica tema salvo no localStorage ao carregar
const savedTheme = localStorage.getItem('theme') || 'dark';
document.documentElement.setAttribute('data-theme', savedTheme);

// Ignora erros de extensões do navegador globalmente
window.addEventListener('error', (event) => {
  if (event.error?.stack?.includes('chrome-extension://') || 
      event.error?.stack?.includes('moz-extension://') ||
      event.message?.includes('Talisman') ||
      event.message?.includes('extension')) {
    event.preventDefault();
    console.warn('Erro de extensão do navegador ignorado:', event.error);
    return false;
  }
}, true);

window.addEventListener('unhandledrejection', (event) => {
  if (event.reason?.stack?.includes('chrome-extension://') || 
      event.reason?.stack?.includes('moz-extension://') ||
      event.reason?.message?.includes('Talisman') ||
      event.reason?.message?.includes('extension')) {
    event.preventDefault();
    console.warn('Promise rejection de extensão ignorada:', event.reason);
    return false;
  }
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);

