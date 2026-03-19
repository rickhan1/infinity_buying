import React from 'react';
import '../Dashboard.css';

export default function SummaryCards({ data, lang }) {
  if (!data) return null;

  const totalCapital = Object.values(data).reduce((acc, curr) => acc + (curr.initial_capital || 100000), 0);
  const totalCost = Object.values(data).reduce((acc, curr) => acc + curr.total_cost, 0);
  const totalEval = Object.values(data).reduce((acc, curr) => {
    const history = curr.history || [];
    if (history.length === 0) return acc;
    const lastClose = history[history.length - 1].closing_price;
    return acc + (curr.total_shares * lastClose);
  }, 0);

  const totalProfit = totalEval - totalCost;
  const totalProfitRatio = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;
  const totalCash = Object.values(data).reduce((acc, curr) => acc + curr.cash_balance, 0);

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
  
  return (
    <div className="summary-container animate-fade-in">
      <div className="glass-panel summary-card">
        <h3>{lang === 'en' ? 'Initial Capital' : '총 투자 원금'}</h3>
        <div className="value">{formatCurrency(totalCapital)}</div>
      </div>
      <div className="glass-panel summary-card">
        <h3>{lang === 'en' ? 'Total Evaluation' : '현재 총 평가금'}</h3>
        <div className="value">{formatCurrency(totalEval)}</div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          {lang === 'en' ? 'Total Cost: ' : '총 매입금: '}{formatCurrency(totalCost)}
        </div>
      </div>
      <div className="glass-panel summary-card">
        <h3>{lang === 'en' ? 'Total Profit/Loss' : '총 손익 현황'}</h3>
        <div className={`value profit ${totalProfit >= 0 ? 'positive' : 'negative'}`}>
          {totalProfit > 0 ? '+' : ''}{formatCurrency(totalProfit)}
        </div>
        <div className={`profit ${totalProfit >= 0 ? 'positive' : 'negative'}`} style={{ fontWeight: 600 }}>
          ({totalProfit > 0 ? '+' : ''}{totalProfitRatio.toFixed(2)}%)
        </div>
      </div>
      <div className="glass-panel summary-card">
        <h3>{lang === 'en' ? 'Cash Balance' : '보유 현금 잔고'}</h3>
        <div className="value">{formatCurrency(totalCash)}</div>
      </div>
    </div>
  );
}
