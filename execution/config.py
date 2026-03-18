"""
config.py — 무한매수법 시뮬레이터 설정값 관리

모든 전략 파라미터와 환경 변수를 중앙에서 관리합니다.
α(알파), 분할수, 익절/손절 비율 등을 여기서 변경하면 전체 시스템에 반영됩니다.
"""

import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# ============================================================
# 전략 설정 (Strategy Parameters)
# ============================================================

# 투자 종목 목록
TICKERS = ["TQQQ", "SOLX"]

# 종목별 초기 자금 (USD)
INITIAL_CAPITAL = 100_000

# 분할 수 (40분할)
NUM_SPLITS = 40

# 1회 매수금 (초기자금 / 분할수)
BUY_AMOUNT_PER_SPLIT = INITIAL_CAPITAL / NUM_SPLITS  # $2,500

# 알파(α) — 평단가 대비 LOC 주문 상한선 비율
# 종가 > 평단가일 때, 평단가 × (1 + ALPHA) 이하면 절반 매수
ALPHA = 0.03  # 3%

# 익절 비율 (+10%)
TAKE_PROFIT_RATIO = 0.10

# 손절 비율 (-10%)
STOP_LOSS_RATIO = -0.10

# ============================================================
# 텔레그램 설정 (Telegram)
# ============================================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ============================================================
# 구글 시트 설정 (Google Sheets)
# ============================================================

GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")
GOOGLE_CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")

# ============================================================
# 데이터 경로 (Data Paths)
# ============================================================

# 프로젝트 루트 디렉토리
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 상태 파일 경로
STATE_FILE = os.path.join(PROJECT_ROOT, "data", "state.json")
