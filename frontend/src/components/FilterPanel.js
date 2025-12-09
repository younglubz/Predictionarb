import React from 'react';
import './FilterPanel.css';

function FilterPanel({ filters, setFilters }) {
  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({
      minProfit: 0,
      minLiquidity: 0,
      exchange: 'all',
      sortBy: 'profit'
    });
  };

  const hasActiveFilters = filters.minProfit > 0 || 
                          filters.minLiquidity > 0 || 
                          filters.exchange !== 'all';

  return (
    <div className="filter-panel">
      <div className="filter-header">
        <h3>🔍 Filtros</h3>
        {hasActiveFilters && (
          <button onClick={resetFilters} className="btn-reset">
            ✕ Limpar Filtros
          </button>
        )}
      </div>
      
      <div className="filter-grid">
        {/* Lucro Mínimo */}
        <div className="filter-item">
          <label htmlFor="minProfit">
            💰 Lucro Mínimo (%)
          </label>
          <input
            id="minProfit"
            type="number"
            min="0"
            max="100"
            step="0.1"
            value={filters.minProfit}
            onChange={(e) => updateFilter('minProfit', parseFloat(e.target.value) || 0)}
            placeholder="0"
          />
          <span className="filter-value">{filters.minProfit}%</span>
        </div>

        {/* Liquidez Mínima */}
        <div className="filter-item">
          <label htmlFor="minLiquidity">
            💧 Liquidez Mínima ($)
          </label>
          <input
            id="minLiquidity"
            type="number"
            min="0"
            step="10"
            value={filters.minLiquidity}
            onChange={(e) => updateFilter('minLiquidity', parseFloat(e.target.value) || 0)}
            placeholder="0"
          />
          <span className="filter-value">${filters.minLiquidity}</span>
        </div>

        {/* Exchange */}
        <div className="filter-item">
          <label htmlFor="exchange">
            🏪 Exchange
          </label>
          <select
            id="exchange"
            value={filters.exchange}
            onChange={(e) => updateFilter('exchange', e.target.value)}
          >
            <option value="all">Todas</option>
            <option value="polymarket">Polymarket</option>
            <option value="manifold">Manifold</option>
            <option value="predictit">PredictIt</option>
            <option value="kalshi">Kalshi</option>
            <option value="polyrouter">PolyRouter</option>
          </select>
        </div>

        {/* Ordenar Por */}
        <div className="filter-item">
          <label htmlFor="sortBy">
            📊 Ordenar Por
          </label>
          <select
            id="sortBy"
            value={filters.sortBy}
            onChange={(e) => updateFilter('sortBy', e.target.value)}
          >
            <option value="profit">Maior Lucro</option>
            <option value="liquidity">Maior Liquidez</option>
            <option value="recent">Mais Recente</option>
          </select>
        </div>
      </div>

      {/* Filtros Rápidos */}
      <div className="quick-filters">
        <h4>⚡ Filtros Rápidos</h4>
        <div className="quick-filter-buttons">
          <button 
            className="quick-filter-btn"
            onClick={() => setFilters({ ...filters, minProfit: 0.5, minLiquidity: 20 })}
          >
            🟢 Relaxado (0.5%, $20)
          </button>
          <button 
            className="quick-filter-btn"
            onClick={() => setFilters({ ...filters, minProfit: 1, minLiquidity: 50 })}
          >
            🟡 Moderado (1%, $50)
          </button>
          <button 
            className="quick-filter-btn"
            onClick={() => setFilters({ ...filters, minProfit: 2, minLiquidity: 100 })}
          >
            🔴 Rigoroso (2%, $100)
          </button>
        </div>
      </div>

      {/* Estatísticas dos Filtros */}
      {hasActiveFilters && (
        <div className="filter-stats">
          <p>✓ Filtros ativos aplicados</p>
        </div>
      )}
    </div>
  );
}

export default FilterPanel;

