"""
update_sheets.py — 구글 스프레드시트 기록 모듈

gspread를 사용하여 매일 매매 기록을 구글 시트에 히스토리로 누적합니다.
TQQQ, SOLX 각각 별도 시트(탭)에 기록합니다.
"""

import gspread
from google.oauth2.service_account import Credentials
import logging
import os
import json

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import GOOGLE_SHEETS_ID, GOOGLE_CREDENTIALS_FILE, PROJECT_ROOT

logger = logging.getLogger(__name__)

# 구글 시트 헤더 정의
HEADERS = [
    "날짜", "종가", "액션", "매수금액", "매수수량",
    "총보유수량", "총매수금", "평단가", "평가금",
    "수익률(%)", "현금잔고", "매수횟수", "사이클"
]

# 액션 값 -> 한국어 표시
ACTION_MAP = {
    "buy_full": "전액매수",
    "buy_half": "절반매수",
    "no_fill": "미체결",
    "wait": "대기",
    "hold": "보유",
    "take_profit": "🟢 익절",
    "stop_loss": "🔴 손절",
}


def get_sheets_client() -> gspread.Client:
    """구글 시트 클라이언트를 생성합니다."""
    # GitHub Actions에서는 환경변수에서 JSON 로드
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        # GitHub Actions 환경: Secrets에서 JSON 문자열 로드
        creds_dict = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )
    else:
        # 로컬 환경: credentials.json 파일 로드
        creds_file = os.path.join(PROJECT_ROOT, GOOGLE_CREDENTIALS_FILE)
        creds = Credentials.from_service_account_file(
            creds_file,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
        )

    return gspread.authorize(creds)


def ensure_worksheet(spreadsheet: gspread.Spreadsheet, ticker: str) -> gspread.Worksheet:
    """종목별 시트(탭)가 없으면 생성하고, 헤더를 설정합니다."""
    try:
        worksheet = spreadsheet.worksheet(ticker)
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title=ticker, rows=1000, cols=len(HEADERS))
        worksheet.append_row(HEADERS)
        logger.info(f"[{ticker}] 새 시트 생성 + 헤더 추가")

    # 헤더가 비어있으면 추가
    first_row = worksheet.row_values(1)
    if not first_row:
        worksheet.append_row(HEADERS)

    return worksheet


def append_record(ticker: str, record: dict, dry_run: bool = False) -> None:
    """
    구글 시트에 매매 기록 1행을 추가합니다.

    Args:
        ticker: 종목 코드
        record: simulate_trade.py에서 생성한 기록 딕셔너리
        dry_run: True면 실제 기록하지 않고 로그만 출력
    """
    row = [
        record["date"],
        record["closing_price"],
        ACTION_MAP.get(record["action"], record["action"]),
        record["buy_amount"],
        round(record["buy_shares"], 4),
        round(record["total_shares"], 4),
        record["total_cost"],
        round(record["avg_price"], 2),
        record["evaluation"],
        round(record["profit_ratio"] * 100, 2),
        record["cash_balance"],
        record["buy_count"],
        record["cycle"],
    ]

    if dry_run:
        logger.info(f"[{ticker}] DRY-RUN 시트 기록: {row}")
        return

    try:
        client = get_sheets_client()
        spreadsheet = client.open_by_key(GOOGLE_SHEETS_ID)
        worksheet = ensure_worksheet(spreadsheet, ticker)
        worksheet.append_row(row, value_input_option="USER_ENTERED")
        logger.info(f"[{ticker}] 구글 시트 기록 완료: {record['date']}")
    except Exception as e:
        logger.error(f"[{ticker}] 구글 시트 기록 실패: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== 구글 시트 모듈 테스트 ===")
    # 테스트용 기록
    test_record = {
        "date": "2026-03-18",
        "closing_price": 50.0,
        "action": "buy_full",
        "buy_amount": 2500.0,
        "buy_shares": 50.0,
        "total_shares": 50.0,
        "total_cost": 2500.0,
        "avg_price": 50.0,
        "evaluation": 2500.0,
        "profit_ratio": 0.0,
        "cash_balance": 97500.0,
        "buy_count": 1,
        "cycle": 1,
    }
    append_record("TQQQ", test_record, dry_run=True)
