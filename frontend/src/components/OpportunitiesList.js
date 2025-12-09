import React from 'react';
import './OpportunitiesList.css';

const OpportunitiesList = ({ opportunities }) => {
  const formatProfit = (value) => {
    return (value * 100).toFixed(2) + '%';
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(value);
  };

  if (opportunities.length === 0) {
    return (
      <div className="opportunities-list">
        <h2>Oportunidades de Arbitragem</h2>
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <p>Nenhuma oportunidade encontrada no momento</p>
          <p className="empty-subtitle">As oportunidades aparecerão aqui quando detectadas</p>
        </div>
      </div>
    );
  }

  return (
    <div className="opportunities-list">
      <h2>Oportunidades de Arbitragem ({opportunities.length})</h2>
      <div className="opportunities-grid">
        {opportunities.map((opp, index) => (
          <div key={index} className="opportunity-card">
            <div className="opportunity-header">
              <div className="profit-badge" style={{
                backgroundColor: (opp.profit_pct || 0) > 0.05 ? '#10b981' : (opp.profit_pct || 0) > 0.02 ? '#f59e0b' : '#ef4444'
              }}>
                {formatProfit(opp.profit_pct || opp.roi || 0)}
              </div>
              <div className="confidence-badge">
                Confiança: {((opp.confidence || 0) * 100).toFixed(0)}%
              </div>
            </div>

            <div className="opportunity-content">
              <div className="trade-section">
                <div className="trade-label">Comprar</div>
                <div className="trade-details">
                  <div className="exchange-name">{opp.buy?.exchange || opp.exchange_a || 'N/A'}</div>
                  <div className="trade-price">{formatCurrency(opp.buy?.price || 0)}</div>
                  <div className="trade-question">{opp.buy?.question || opp.market_a?.question || 'N/A'}</div>
                  {(opp.buy?.url || opp.market_a?.url) && (
                    <a href={opp.buy?.url || opp.market_a?.url} target="_blank" rel="noopener noreferrer" className="trade-link">
                      Ver mercado →
                    </a>
                  )}
                </div>
              </div>

              <div className="trade-arrow">→</div>

              <div className="trade-section">
                <div className="trade-label">Vender</div>
                <div className="trade-details">
                  <div className="exchange-name">{opp.sell?.exchange || opp.exchange_b || 'N/A'}</div>
                  <div className="trade-price">{formatCurrency(opp.sell?.price || 0)}</div>
                  <div className="trade-question">{opp.sell?.question || opp.market_b?.question || 'N/A'}</div>
                  {(opp.sell?.url || opp.market_b?.url) && (
                    <a href={opp.sell?.url || opp.market_b?.url} target="_blank" rel="noopener noreferrer" className="trade-link">
                      Ver mercado →
                    </a>
                  )}
                </div>
              </div>
            </div>

            <div className="opportunity-footer">
              <div className="profit-details">
                <div className="profit-item">
                  <span className="profit-label">Lucro Líquido:</span>
                  <span className="profit-value">{formatCurrency(opp.net_profit || 0)}</span>
                </div>
                <div className="profit-item">
                  <span className="profit-label">Taxas:</span>
                  <span className="profit-value">{formatCurrency(opp.fees || 0)}</span>
                </div>
                <div className="profit-item">
                  <span className="profit-label">Liquidez:</span>
                  <span className="profit-value">
                    {formatCurrency(Math.min(
                      opp.buy?.liquidity || opp.market_a?.liquidity || 0,
                      opp.sell?.liquidity || opp.market_b?.liquidity || 0
                    ))}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OpportunitiesList;

