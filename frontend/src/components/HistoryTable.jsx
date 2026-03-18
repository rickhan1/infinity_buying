import React from 'react';
import '../Dashboard.css';

const ACTION_LABELS_KO = {
  buy_full: '전액매수',
  buy_half: '절반매수',
  unfilled: '미체결',
  sell_profit: '익절',
  sell_loss: '손절'
};

const ACTION_LABELS_EN = {
  buy_full: 'Full Buy',
  buy_half: 'Half Buy',
  unfilled: 'Unfilled',
  sell_profit: 'Take Profit',
  sell_loss: 'Stop Loss'
};

export default function HistoryTable({ history, lang }) {
  if (!history || history.length === 0) {
    return <div style={{ color: 'var(--text-secondary)' }}>{lang === 'en' ? 'No data.' : '데이터가 없습니다.'}</div>;
  }

  const reversedHistory = [...history].reverse();
  const labels = lang === 'en' ? ACTION_LABELS_EN : ACTION_LABELS_KO;

  return (
    <div className="glass-panel animate-fade-in" style={{ animationDelay: '0.3s' }}>
      <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: 600 }}>
        {lang === 'en' ? 'Detailed Transaction History' : '상세 거래 히스토리'}
      </h2>
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>{lang === 'en' ? 'Date' : '날짜'}</th>
              <th>{lang === 'en' ? 'Action' : '액션'}</th>
              <th>{lang === 'en' ? 'Close' : '종가'}</th>
              <th>{lang === 'en' ? 'Amount' : '매수/매도액'}</th>
              <th>{lang === 'en' ? 'Shares Chg' : '수량 변동'}</th>
              <th>{lang === 'en' ? 'Total Shares' : '보유 수량'}</th>
              <th>{lang === 'en' ? 'Avg Price' : '평단가'}</th>
              <th>{lang === 'en' ? 'Cycle/Count' : '진행 회차'}</th>
            </tr>
          </thead>
          <tbody>
            {reversedHistory.map((item, idx) => (
              <tr key={idx}>
                <td>{item.date}</td>
                <td>
                  <span className={`action-badge action-${item.action}`}>
                    {labels[item.action] || item.action}
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
