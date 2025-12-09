import React from 'react';
import './StatsPanel.css';

const StatsPanel = ({ stats }) => {
  if (!stats) return null;

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="stats-panel">
      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-content">
          <div className="stat-value">{stats.total_markets || 0}</div>
          <div className="stat-label">Mercados Ativos</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">💰</div>
        <div className="stat-content">
          <div className="stat-value">{formatCurrency(stats.total_volume_24h || 0)}</div>
          <div className="stat-label">Volume 24h</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">💎</div>
        <div className="stat-content">
          <div className="stat-value">{formatCurrency(stats.total_liquidity || 0)}</div>
          <div className="stat-label">Liquidez Total</div>
        </div>
      </div>

      <div className="stat-card highlight">
        <div className="stat-icon">🚀</div>
        <div className="stat-content">
          <div className="stat-value">{stats.opportunities_count || 0}</div>
          <div className="stat-label">Oportunidades</div>
        </div>
      </div>

      {stats.by_exchange && (
        <div className="stat-card exchanges">
          <div className="stat-icon">🏢</div>
          <div className="stat-content">
            <div className="stat-value">{Object.keys(stats.by_exchange).length}</div>
            <div className="stat-label">Exchanges</div>
            <div className="exchange-list">
              {Object.entries(stats.by_exchange).map(([name, data]) => (
                <div key={name} className="exchange-item">
                  <span className="exchange-name">{name}</span>
                  <span className="exchange-count">{data.count} mercados</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsPanel;

