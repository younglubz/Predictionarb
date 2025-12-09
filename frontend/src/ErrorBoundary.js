import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Atualiza o state para exibir a UI de fallback
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Filtra erros de extensões do navegador
    const isExtensionError = error?.stack?.includes('chrome-extension://') || 
                            error?.stack?.includes('moz-extension://') ||
                            error?.message?.includes('extension');
    
    if (isExtensionError) {
      // Ignora erros de extensões e não mostra o erro
      console.warn('Erro de extensão do navegador ignorado:', error);
      this.setState({ hasError: false });
      return;
    }
    
    // Log de outros erros
    console.error('Erro capturado pelo ErrorBoundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Verifica se é erro de extensão
      const isExtensionError = this.state.error?.stack?.includes('chrome-extension://') || 
                              this.state.error?.stack?.includes('moz-extension://');
      
      if (isExtensionError) {
        // Retorna os children normalmente se for erro de extensão
        return this.props.children;
      }
      
      // Mostra UI de erro apenas para erros reais
      return (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: '#fff',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>⚠️ Erro na Aplicação</h1>
          <p style={{ fontSize: '1.1rem', marginBottom: '2rem' }}>
            Ocorreu um erro inesperado. Por favor, recarregue a página.
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '0.75rem 2rem',
              fontSize: '1rem',
              background: '#fff',
              color: '#667eea',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Recarregar Página
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

