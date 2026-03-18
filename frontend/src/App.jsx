import React, { useState, useEffect } from 'react'
import './index.css'
import './Dashboard.css'
import SummaryCards from './components/SummaryCards'
import InteractiveChart from './components/InteractiveChart'
import HistoryTable from './components/HistoryTable'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('TQQQ')

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('https://raw.githubusercontent.com/rickhan1/infinity_buying/main/data/state.json')
        if (!response.ok) throw new Error('Failed to fetch state data.')
        const result = await response.json()
        setData(result)
        // Set first key as active tab if 'TQQQ' doesn't exist
        if (!result['TQQQ']) {
          setActiveTab(Object.keys(result)[0])
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="app-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <h2 className="text-gradient">데이터 불러오는 중...</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="glass-panel" style={{ color: 'var(--accent-red)' }}>
          <h2>에러 발생</h2>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  const currentHistory = data[activeTab]?.history || []

  return (
    <div className="app-container">
      <h1 className="title text-gradient">Infinity Buying 실시간 대시보드</h1>
      
      {/* 최고 상단 통합 요약 카드 */}
      <SummaryCards data={data} />

      {/* 종목 탭 셀렉터 */}
      <div style={{ marginTop: '3rem' }}>
        <div className="tab-buttons animate-fade-in">
          {Object.keys(data).map(ticker => (
            <button 
              key={ticker}
              className={`tab-btn ${activeTab === ticker ? 'active' : ''}`}
              onClick={() => setActiveTab(ticker)}
            >
              {ticker}
            </button>
          ))}
        </div>

        {/* 선택된 종목의 챠트와 히스토리 표 */}
        {currentHistory.length > 0 ? (
          <>
            <InteractiveChart history={currentHistory} />
            <HistoryTable history={currentHistory} />
          </>
        ) : (
          <div className="glass-panel animate-fade-in">이 종목의 시뮬레이션 히스토리가 아직 없습니다.</div>
        )}
      </div>
    </div>
  )
}

export default App
