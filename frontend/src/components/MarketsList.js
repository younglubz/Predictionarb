import React, { useState } from 'react';
import './MarketsList.css';

const MarketsList = ({ markets }) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const exchanges = [...new Set(markets.map(m => m.exchange))];
  
  const filteredMarkets = markets.filter(market => {
    const matchesFilter = filter === 'all' || market.exchange === filter;
    const matchesSearch = market.question.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  return (
    <div className="markets-list">
      <h2>Mercados ({markets.length})</h2>
      
      <div className="markets-filters">
        <input
          type="text"
          placeholder="Buscar mercado..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="filter-select"
        >
          <option value="all">Todas as exchanges</option>
          {exchanges.map(ex => (
            <option key={ex} value={ex}>{ex}</option>
          ))}
        </select>
      </div>

      <div className="markets-grid">
        {filteredMarkets.slice(0, 50).map((market, index) => (
          <div key={index} className="market-card">
            <div className="market-header">
              <span className="market-exchange">{market.exchange}</span>
              <span className={`market-outcome ${market.outcome.toLowerCase()}`}>
                {market.outcome}
              </span>
            </div>
            
            <div className="market-question">{market.question}</div>
            
            <div className="market-details">
              <div className="market-detail">
                <span className="detail-label">Preço:</span>
                <span className="detail-value">{formatCurrency(market.price)}</span>
              </div>
              <div className="market-detail">
                <span className="detail-label">Liquidez:</span>
                <span className="detail-value">{formatCurrency(market.liquidity)}</span>
              </div>
              <div className="market-detail">
                <span className="detail-label">Volume 24h:</span>
                <span className="detail-value">{formatCurrency(market.volume_24h)}</span>
              </div>
            </div>

            {market.url && (
              <a
                href={market.url}
                target="_blank"
                rel="noopener noreferrer"
                className="market-link"
              >
                Ver mercado →
              </a>
            )}
          </div>
        ))}
      </div>

      {filteredMarkets.length === 0 && (
        <div className="empty-state">
          <p>Nenhum mercado encontrado</p>
        </div>
      )}
    </div>
  );
};

export default MarketsList;

