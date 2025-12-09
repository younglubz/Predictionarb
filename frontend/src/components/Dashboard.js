import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import './Dashboard.css';

const Dashboard = ({ opportunities }) => {
  // Agrupa oportunidades por exchange
  const exchangeData = opportunities.reduce((acc, opp) => {
    const buyExchange = opp.buy?.exchange || opp.exchange_a || 'Unknown';
    const sellExchange = opp.sell?.exchange || opp.exchange_b || 'Unknown';
    
    if (!acc[buyExchange]) acc[buyExchange] = { name: buyExchange, count: 0, totalProfit: 0 };
    if (!acc[sellExchange]) acc[sellExchange] = { name: sellExchange, count: 0, totalProfit: 0 };
    
    acc[buyExchange].count += 1;
    acc[buyExchange].totalProfit += opp.net_profit || 0;
    acc[sellExchange].count += 1;
    acc[sellExchange].totalProfit += opp.net_profit || 0;
    
    return acc;
  }, {});

  const chartData = Object.values(exchangeData).map(ex => ({
    name: ex.name,
    oportunidades: ex.count,
    lucro: parseFloat(ex.totalProfit.toFixed(2))
  }));

  // Top 5 oportunidades por lucro
  const topOpportunities = [...opportunities]
    .sort((a, b) => {
      const profitA = a.profit_pct || a.roi || 0;
      const profitB = b.profit_pct || b.roi || 0;
      return profitB - profitA;
    })
    .slice(0, 5)
    .map(opp => {
      const question = opp.buy?.question || opp.market_a?.question || 'N/A';
      const profit = opp.profit_pct || opp.roi || 0;
      return {
        name: question.substring(0, 30) + (question.length > 30 ? '...' : ''),
        lucro: parseFloat((profit * 100).toFixed(2))
      };
    });

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];

  return (
    <div className="dashboard">
      <div className="dashboard-card">
        <h2>Oportunidades por Exchange</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="name" stroke="white" />
            <YAxis stroke="white" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.8)', 
                border: 'none', 
                borderRadius: '8px',
                color: 'white'
              }} 
            />
            <Bar dataKey="oportunidades" fill="#667eea" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="dashboard-card">
        <h2>Top 5 Oportunidades</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={topOpportunities} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis type="number" stroke="white" />
            <YAxis dataKey="name" type="category" stroke="white" width={150} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'rgba(0,0,0,0.8)', 
                border: 'none', 
                borderRadius: '8px',
                color: 'white'
              }}
              formatter={(value) => `${value.toFixed(2)}%`}
            />
            <Bar dataKey="lucro" fill="#764ba2" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Dashboard;

