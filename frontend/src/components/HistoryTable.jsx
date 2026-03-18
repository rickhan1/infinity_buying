import React from 'react';
import '../Dashboard.css';

const ACTION_LABELS = {
  buy_full: '전액매수',
  buy_half: '절반매수',
  unfilled: '미체결',
  sell_profit: '익절',
  sell_loss: '손절'
};

export default function HistoryTable({ history }) {
  if (!history || history.length === 0) {
    return <div style={{ color: 'var(--text-secondary)' }}>데이터가 없습니다.</div>;
  }

  // 최신 데이터가 위로 오게 역순 정렬
  const reversedHistory = [...history].reverse();

  return (
    <div className="glass-panel animate-fade-in" style={{ animationDelay: '0.3s' }}>
      <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: 600 }}>상세 거래 히스토리</h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>날짜</th>
              <th>액션</th>
              <th>종가</th>
              <th>매수/매도액</th>
              <th>수량 변동</th>
              <th>보유 수량</th>
              <th>평단가</th>
              <th>진행 회차</th>
            </tr>
          </thead>
          <tbody>
            {reversedHistory.map((item, idx) => (
              <tr key={idx}>
                <td>{item.date}</td>
                <td>
                  <span className={`action-badge action-${item.action}`}>
                    {ACTION_LABELS[item.action] || item.action}
                  </span>
                </td>
                <td>${item.closing_price.toFixed(2)}</td>
                <td>{item.buy_amount > 0 ? `$${item.buy_amount.toFixed(2)}` : '-'}</td>
                <td>{item.buy_shares > 0 ? `+${item.buy_shares.toFixed(4)}` : '-'}</td>
                <td>{item.total_shares.toFixed(4)}</td>
                <td>${item.avg_price.toFixed(2)}</td>
                <td>{item.buy_count} / 40</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
