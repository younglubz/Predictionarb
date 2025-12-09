import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import './App.css';
import Dashboard from './components/Dashboard';
import StatsPanel from './components/StatsPanel';
import OpportunitiesList from './components/OpportunitiesList';
import MarketsList from './components/MarketsList';
import FilterPanel from './components/FilterPanel';
import ErrorBoundary from './ErrorBoundary';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [opportunities, setOpportunities] = useState([]);
  const [stats, setStats] = useState(null);
  const [markets, setMarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [activeTab, setActiveTab] = useState('opportunities');
  const [filters, setFilters] = useState({
    minProfit: 0,
    minLiquidity: 0,
    exchange: 'all',
    sortBy: 'profit'
  });

  // Carrega dados com prioridade (stats primeiro, depois opportunities, markets por último)
  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Primeiro carrega stats (mais rápido)
      const statsRes = await axios.get(`${API_BASE}/stats`, { timeout: 3000 })
        .catch(() => ({ data: {} }));
      setStats(statsRes.data);
      setLoading(false); // Libera UI com stats
      
      // Depois carrega opportunities
      const oppsRes = await axios.get(`${API_BASE}/opportunities`, { timeout: 5000 })
        .catch(() => ({ data: { opportunities: [] } }));
      setOpportunities(oppsRes.data.opportunities || []);
      setLastUpdate(oppsRes.data.last_update);
      
      // Por último carrega markets (pode ser pesado)
      const marketsRes = await axios.get(`${API_BASE}/markets`, { timeout: 10000 })
        .catch(() => ({ data: { markets: [] } }));
      setMarkets(marketsRes.data.markets || []);
      
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();

    // WebSocket com reconnect otimizado
    let ws = null;
    let reconnectTimeout = null;
    
    const connectWebSocket = () => {
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsHost = process.env.REACT_APP_WS_URL || 'localhost:8000';
      
      try {
        ws = new WebSocket(`${wsProtocol}//${wsHost}/ws`);
        
        ws.onopen = () => {
          console.log('WebSocket conectado');
          setWsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            setOpportunities(prev => data.opportunities || prev);
            setLastUpdate(data.last_update);
          } catch (error) {
            console.error('Erro ao processar WebSocket:', error);
          }
        };

        ws.onerror = () => {
          setWsConnected(false);
        };

        ws.onclose = () => {
          setWsConnected(false);
          // Reconnect após 5s
          reconnectTimeout = setTimeout(connectWebSocket, 5000);
        };
      } catch (error) {
        console.error('Erro ao conectar WebSocket:', error);
      }
    };

    connectWebSocket();

    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [loadData]);

  // Memoiza filtragem para evitar recalcular a cada render
  const filteredOpportunities = useMemo(() => {
    return opportunities.filter(opp => {
      if (filters.minProfit > 0 && opp.roi < filters.minProfit) return false;
      if (filters.exchange !== 'all' && 
          opp.exchange_a !== filters.exchange && 
          opp.exchange_b !== filters.exchange) return false;
      return true;
    }).sort((a, b) => {
      if (filters.sortBy === 'profit') return b.roi - a.roi;
      if (filters.sortBy === 'liquidity') {
        const liquidityA = Math.min(a.market_a?.liquidity || 0, a.market_b?.liquidity || 0);
        const liquidityB = Math.min(b.market_a?.liquidity || 0, b.market_b?.liquidity || 0);
        return liquidityB - liquidityA;
      }
      return 0;
    });
  }, [opportunities, filters]);

  // Memoiza filtragem de mercados
  const filteredMarkets = useMemo(() => {
    return markets.filter(market => {
      if (filters.minLiquidity > 0 && market.liquidity < filters.minLiquidity) return false;
      if (filters.exchange !== 'all' && market.exchange !== filters.exchange) return false;
      return true;
    });
  }, [markets, filters.minLiquidity, filters.exchange]);

  const handleRefresh = useCallback(() => {
    setLoading(true);
    loadData();
  }, [loadData]);

  const handleExport = useCallback(() => {
    const dataStr = JSON.stringify({ 
      opportunities: filteredOpportunities, 
      markets: filteredMarkets, 
      stats,
      exportedAt: new Date().toISOString()
    }, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `arbitrage-data-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [filteredOpportunities, filteredMarkets, stats]);

  return (
    <ErrorBoundary>
      <div className="App">
        <header className="app-header">
          <div className="header-content">
            <div className="header-left">
              <h1>🚀 Prediction Market Arbitrage</h1>
              <div className="header-status">
                <span className={`status-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
                  {wsConnected ? '●' : '○'}
                </span>
                <span>{wsConnected ? 'Conectado' : 'Desconectado'}</span>
                {lastUpdate && (
                  <span className="last-update">
                    Última atualização: {new Date(lastUpdate).toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>
            <div className="header-actions">
              <button onClick={handleRefresh} className="btn-primary" disabled={loading}>
                🔄 {loading ? 'Atualizando...' : 'Atualizar'}
              </button>
              <button onClick={handleExport} className="btn-secondary">
                📥 Exportar
              </button>
            </div>
          </div>
        </header>

        {/* Tabs de Navegação */}
        <nav className="nav-tabs">
          <button 
            className={activeTab === 'opportunities' ? 'tab-active' : 'tab'}
            onClick={() => setActiveTab('opportunities')}
          >
            🎯 Oportunidades ({filteredOpportunities.length})
          </button>
          <button 
            className={activeTab === 'markets' ? 'tab-active' : 'tab'}
            onClick={() => setActiveTab('markets')}
          >
            📊 Mercados ({filteredMarkets.length})
          </button>
          <button 
            className={activeTab === 'stats' ? 'tab-active' : 'tab'}
            onClick={() => setActiveTab('stats')}
          >
            📈 Estatísticas
          </button>
        </nav>

        <main className="app-main">
          {loading && !stats ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Carregando dados...</p>
            </div>
          ) : (
            <>
              <FilterPanel filters={filters} setFilters={setFilters} />
              
              {activeTab === 'opportunities' && (
                <>
                  <Dashboard opportunities={filteredOpportunities} />
                  <OpportunitiesList opportunities={filteredOpportunities} />
                </>
              )}
              
              {activeTab === 'markets' && (
                <MarketsList markets={filteredMarkets} />
              )}
              
              {activeTab === 'stats' && (
                <StatsPanel stats={stats} opportunities={opportunities} markets={markets} />
              )}
            </>
          )}
        </main>

        <footer className="app-footer">
          <p>Sistema de Arbitragem em Prediction Markets</p>
          <p>
            {markets.length} mercados | {opportunities.length} oportunidades | 
            Filtros: {filters.minProfit}% lucro, ${filters.minLiquidity} liquidez
          </p>
        </footer>
      </div>
    </ErrorBoundary>
  );
}

export default App;

