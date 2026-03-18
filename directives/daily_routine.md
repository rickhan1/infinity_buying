# 일일 실행 루틴 SOP

## 실행 시점
- 매일 미국 장 마감 30분 후 (EDT 4:30 PM / EST 4:30 PM)
- 평일만 실행 (월~금)
- GitHub Actions Cron으로 자동 트리거

## 실행 순서

### Step 1: 데이터 수집
- **스크립트**: `execution/fetch_stock_data.py`
- **동작**: yfinance로 TQQQ, SOLX 당일 종가 수집
- **실패 시**: 에러 로그 + 텔레그램 알림 후 종료

### Step 2: 매매 판단
- **스크립트**: `execution/simulate_trade.py`
- **동작**: 각 종목별 LOC 매수 로직 실행, 익절/손절 판단
- **입력**: state.json (현재 포지션), 당일 종가
- **출력**: 업데이트된 포지션 데이터

### Step 3: 상태 저장 (Git)
- **파일**: `data/state.json`
- **동작**: 매매 결과를 JSON에 반영

### Step 4: 구글 시트 기록
- **스크립트**: `execution/update_sheets.py`
- **동작**: 히스토리 행 추가 (차트용 누적 데이터)

### Step 5: 텔레그램 알림
- **스크립트**: `execution/send_notification.py`
- **동작**: 일일 리포트 전송

### Step 6: Git 커밋 & 푸시
- **동작**: state.json 변경 사항 자동 커밋
- GitHub Actions 워크플로우에서 처리

## 에러 처리
- 각 Step에서 에러 발생 시 텔레그램으로 에러 알림 전송
- 데이터 수집 실패 시 나머지 Step 스킵
- 구글 시트/알림 실패 시 state.json은 이미 저장된 상태이므로 다음 날 정상 진행 가능
