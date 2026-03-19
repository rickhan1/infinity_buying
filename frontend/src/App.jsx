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
  const [lang, setLang] = useState('ko')

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('lang') === 'en') {
      setLang('en');
    }
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 로컬 환경(GitHub Actions 임시 렌더러 포함)에서는 빌드 전 복사된 최신 로컬 캐시를 읽고,
        // 실서버 깃허브 페이지에서는 클라우드 주소를 읽도록 분기처리하여 CDN 지연(Race condition) 타임아웃 붕괴를 완벽 차단.
        const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
        // GitHub Actions 및 로컬 환경에서는 Vite Base URL을 포함한 절대 경로로 접근하여 404 방어
        const url = isLocal
          ? '/infinity_buying/data/state.json'
          : `https://raw.githubusercontent.com/rickhan1/infinity_buying/main/data/state.json`; // The instruction's remote URL had ?t=, but the fetch call below also adds it. I'll keep the base URL here.

        const response = await fetch(url + '?t=' + new Date().getTime()) // 캐시 무력화
        if (!response.ok) throw new Error('Failed to fetch state data.')
        const result = await response.json()
        setData(result)
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
        <h2 className="text-gradient">{lang === 'en' ? 'Loading Data...' : '데이터 불러오는 중...'}</h2>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app-container">
        <div className="glass-panel" style={{ color: 'var(--accent-red)' }}>
          <h2>{lang === 'en' ? 'Error occurred' : '에러 발생'}</h2>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  const currentHistory = data[activeTab]?.history || []

  return (
    <div className="app-container">
      <h1 className="title text-gradient">
        {lang === 'en' ? 'Infinity Buying Live Dashboard' : 'Infinity Buying 실시간 대시보드'}
      </h1>
      
      <SummaryCards data={data} lang={lang} />

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

        {currentHistory.length > 0 ? (
          <>
            <InteractiveChart history={currentHistory} lang={lang} />
            <HistoryTable history={currentHistory} lang={lang} />
          </>
        ) : (
          <div className="glass-panel animate-fade-in">
            {lang === 'en' ? 'No simulation history available for this ticker yet.' : '이 종목의 시뮬레이션 히스토리가 아직 없습니다.'}
          </div>
        )}
      </div>
    </div>
  )
}

export default App
