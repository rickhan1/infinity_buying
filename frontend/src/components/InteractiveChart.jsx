import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot
} from 'recharts';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="glass-panel" style={{ padding: '1rem', border: '1px solid var(--glass-border)' }}>
        <p style={{ fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>{label}</p>
        <p style={{ color: 'var(--accent-cyan)' }}>종가: ${data.closing_price.toFixed(2)}</p>
        <p style={{ color: 'var(--accent-purple)' }}>평단가: ${data.avg_price.toFixed(2)}</p>
        
        {data.action && data.action !== 'unfilled' && (
          <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--glass-border)' }}>
            <p style={{ color: 'var(--text-secondary)' }}>
              액션: <strong style={{ color: 'var(--text-primary)' }}>{data.action}</strong>
            </p>
            {data.buy_amount > 0 && <p>매수금액: ${data.buy_amount.toFixed(2)}</p>}
            {data.buy_shares > 0 && <p>매수수량: {data.buy_shares.toFixed(4)}주</p>}
            <p>총 보유량: {data.total_shares.toFixed(4)}주</p>
            <p style={{ color: data.profit_ratio < 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
              손익: {(data.profit_ratio * 100).toFixed(2)}%
            </p>
          </div>
        )}
      </div>
    );
  }
  return null;
};

export default function InteractiveChart({ history }) {
  if (!history || history.length === 0) return <div style={{ color: 'var(--text-secondary)' }}>차트를 그릴 데이터가 없습니다.</div>;

  return (
    <div className="glass-panel animate-fade-in" style={{ animationDelay: '0.2s', marginTop: '1.5rem', marginBottom: '1.5rem', width: '100%', height: 400 }}>
      <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: 600 }}>종가 & 평단가 추이</h2>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={history} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
          <XAxis dataKey="date" stroke="var(--text-secondary)" fontSize={12} tickMargin={10} minTickGap={30} />
          <YAxis domain={['auto', 'auto']} stroke="var(--text-secondary)" fontSize={12} tickFormatter={(val) => `$${val}`} />
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'rgba(255,255,255,0.2)', strokeWidth: 1, strokeDasharray: '5 5' }} />
          
          {/* 종가 영역 챠트 */}
          <Area 
            type="monotone" 
            dataKey="closing_price" 
            stroke="var(--accent-cyan)" 
            strokeWidth={3}
            fillOpacity={1} 
            fill="url(#colorPrice)" 
            isAnimationActive={true}
          />
          
          {/* 주요 매매 시그널 점 표시 */}
          {history.map((entry, index) => {
            if (entry.action === 'buy_full' || entry.action === 'buy_half') {
              return <ReferenceDot key={`dot-${index}`} x={entry.date} y={entry.closing_price} r={4} fill="var(--accent-green)" stroke="none" />
            }
            if (entry.action.startsWith('sell_')) {
              return <ReferenceDot key={`dot-${index}`} x={entry.date} y={entry.closing_price} r={6} fill="var(--accent-red)" stroke="#fff" strokeWidth={2} />
            }
            return null;
          })}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
