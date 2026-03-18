import React from 'react';
import '../Dashboard.css';

export default function SummaryCards({ data }) {
  if (!data) return null;

  // 총 투자금 계산 (모든 종목의 초기 자금 합계)
  const totalCapital = Object.values(data).reduce((acc, curr) => acc + curr.initial_capital, 0);
  
  // 현재 총 매입금 (모든 종목의 total_cost 합계)
  const totalCost = Object.values(data).reduce((acc, curr) => acc + curr.total_cost, 0);

  // 현재 총 평가금 계산: 평단가 대신, 가장 마지막 종가를 기준으로 총 수량을 곱한 값 이용
  const totalEval = Object.values(data).reduce((acc, curr) => {
    const history = curr.history || [];
    if (history.length === 0) return acc;
    const lastClose = history[history.length - 1].closing_price;
    return acc + (curr.total_shares * lastClose);
  }, 0);

  // 총 수익 및 수익률
  const totalProfit = totalEval - totalCost;
  const totalProfitRatio = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;

  // 전체 잔고
  const totalCash = Object.values(data).reduce((acc, curr) => acc + curr.cash_balance, 0);

  const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);
  
  return (
    <div className="summary-container animate-fade-in">
      <div className="glass-panel summary-card">
        <h3>총 투자 원금 (Initial Capital)</h3>
        <div className="value">{formatCurrency(totalCapital)}</div>
      </div>
      <div className="glass-panel summary-card">
        <h3>현재 총 평가금 (Total Evaluation)</h3>
        <div className="value">{formatCurrency(totalEval)}</div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
          총 매입금: {formatCurrency(totalCost)}
        </div>
      </div>
      <div className="glass-panel summary-card">
        <h3>총 손익 현황 (Total Profit/Loss)</h3>
        <div className={`value profit ${totalProfit >= 0 ? 'positive' : 'negative'}`}>
          {totalProfit > 0 ? '+' : ''}{formatCurrency(totalProfit)}
        </div>
        <div className={`profit ${totalProfit >= 0 ? 'positive' : 'negative'}`} style={{ fontWeight: 600 }}>
          ({totalProfit > 0 ? '+' : ''}{totalProfitRatio.toFixed(2)}%)
        </div>
      </div>
      <div className="glass-panel summary-card">
        <h3>보유 현금 잔고 (Cash Balance)</h3>
        <div className="value">{formatCurrency(totalCash)}</div>
      </div>
    </div>
  );
}
