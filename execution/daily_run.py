"""
daily_run.py — 메인 오케스트레이터

매일 실행되며, 데이터 수집 → 매매 판단 → 상태 저장 → 구글 시트 기록 → 텔레그램 알림 순서로 처리합니다.
GitHub Actions에서 호출되는 진입점입니다.
"""

import argparse
import logging
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TICKERS
from fetch_stock_data import get_closing_prices, get_latest_trade_date
from simulate_trade import load_state, save_state, process_ticker
from update_sheets import append_record
from send_notification import send_daily_report, send_error_notification

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main(dry_run: bool = False, date: str | None = None) -> None:
    """
    일일 매매 시뮬레이션을 실행합니다.

    Args:
        dry_run: True면 실제 시트 기록/알림 전송 없이 로직만 실행
        date: 특정 날짜로 실행 (YYYY-MM-DD). None이면 최근 거래일.
    """
    logger.info("=" * 60)
    logger.info("🚀 무한매수법 시뮬레이터 시작")
    if dry_run:
        logger.info("⚠️  DRY-RUN 모드 (시트 기록/알림 없음)")
    logger.info("=" * 60)

    try:
        # ──────────────────────────────────────────
        # Step 1: 거래일 확인 & 종가 수집
        # ──────────────────────────────────────────
        trade_date = date or get_latest_trade_date()
        if not trade_date:
            logger.warning("거래일 정보를 가져올 수 없습니다. 종료합니다.")
            return

        logger.info(f"📅 거래일: {trade_date}")

        prices = get_closing_prices(TICKERS, trade_date)
        if all(p is None for p in prices.values()):
            logger.warning("모든 종목의 종가 데이터를 가져올 수 없습니다. 비거래일 가능성.")
            return

        # ──────────────────────────────────────────
        # Step 2: 상태 로드
        # ──────────────────────────────────────────
        state = load_state()

        # ──────────────────────────────────────────
        # Step 3: 각 종목별 매매 로직 실행
        # ──────────────────────────────────────────
        daily_records = {}

        for ticker in TICKERS:
            price = prices.get(ticker)
            if price is None:
                logger.warning(f"[{ticker}] 종가 없음 — 스킵")
                continue

            # 중복 실행 방지: 같은 날짜에 이미 기록이 있는지 확인
            if state[ticker]["history"]:
                last_date = state[ticker]["history"][-1].get("date")
                if last_date == trade_date:
                    logger.warning(f"[{ticker}] {trade_date} 이미 처리됨 — 스킵")
                    continue

            state[ticker] = process_ticker(ticker, state[ticker], price, trade_date)

            # 가장 최근 기록을 daily_records에 저장
            if state[ticker]["history"]:
                daily_records[ticker] = state[ticker]["history"][-1]

        if not daily_records:
            logger.info("처리할 종목이 없습니다. 종료합니다.")
            return

        # ──────────────────────────────────────────
        # Step 4: 상태 저장 (Git용)
        # ──────────────────────────────────────────
        save_state(state)

        # ──────────────────────────────────────────
        # Step 5: 구글 시트 기록
        # ──────────────────────────────────────────
        for ticker, record in daily_records.items():
            try:
                append_record(ticker, record, dry_run=dry_run)
            except Exception as e:
                logger.error(f"[{ticker}] 구글 시트 기록 실패: {e}")
                # 시트 기록 실패해도 계속 진행

        # ──────────────────────────────────────────
        # Step 6: 텔레그램 알림
        # ──────────────────────────────────────────
        send_daily_report(daily_records, trade_date, dry_run=dry_run)

        logger.info("=" * 60)
        logger.info("✅ 무한매수법 시뮬레이터 완료")
        logger.info("=" * 60)

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        logger.error(f"치명적 에러 발생:\n{error_msg}")
        if not dry_run:
            send_error_notification(str(e))
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="무한매수법 시뮬레이터")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="DRY-RUN 모드: 시트 기록/알림 없이 로직만 실행",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="특정 날짜로 실행 (YYYY-MM-DD)",
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run, date=args.date)
