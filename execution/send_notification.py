"""
send_notification.py — 텔레그램 알림 전송 모듈

텔레그램 Bot API를 사용하여 일일 매매 리포트를 전송합니다.
"""

import requests
import logging
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


def send_telegram(message: str, parse_mode: str = "HTML") -> bool:
    """
    텔레그램으로 메시지를 전송합니다.

    Args:
        message: 전송할 메시지 (HTML 형식 지원)
        parse_mode: 파싱 모드 ("HTML" 또는 "Markdown")

    Returns:
        성공 여부
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("텔레그램 설정 없음 — 알림 스킵")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("텔레그램 알림 전송 성공")
        return True
    except Exception as e:
        logger.error(f"텔레그램 알림 전송 실패: {e}")
        return False


def format_daily_report(records: dict[str, dict], trade_date: str) -> str:
    """
    일일 매매 리포트 메시지를 생성합니다.

    Args:
        records: {ticker: record} 딕셔너리
        trade_date: 거래일

    Returns:
        HTML 형식의 리포트 문자열
    """
    action_emoji = {
        "buy_full": "📥 전액매수",
        "buy_half": "📥 절반매수",
        "no_fill": "⏸ 미체결",
        "wait": "⏳ 대기",
        "hold": "📊 보유",
        "take_profit": "🟢 익절!!",
        "stop_loss": "🔴 손절!!",
    }

    lines = [
        f"<b>📈 무한매수법 일일 리포트</b>",
        f"<b>📅 {trade_date}</b>",
        "",
    ]

    for ticker, record in records.items():
        action = action_emoji.get(record["action"], record["action"])
        profit_pct = record["profit_ratio"] * 100

        lines.extend([
            f"<b>━━━ {ticker} ━━━</b>",
            f"종가: <b>${record['closing_price']:.2f}</b>",
            f"액션: {action}",
        ])

        if record["buy_amount"] > 0:
            lines.append(f"매수: ${record['buy_amount']:.2f} ({record['buy_shares']:.4f}주)")

        lines.extend([
            f"보유: {record['total_shares']:.4f}주",
            f"평단가: ${record['avg_price']:.2f}",
            f"평가금: ${record['evaluation']:.2f}",
            f"수익률: <b>{profit_pct:+.2f}%</b>",
            f"현금잔고: ${record['cash_balance']:.2f}",
            f"매수횟수: {record['buy_count']}/{40}회 (사이클 #{record['cycle']})",
            "",
        ])

    return "\n".join(lines)


def send_error_notification(error_msg: str) -> bool:
    """에러 발생 시 알림을 전송합니다."""
    message = (
        f"<b>🚨 무한매수법 시뮬레이터 에러</b>\n\n"
        f"<pre>{error_msg}</pre>"
    )
    return send_telegram(message)


def send_daily_report(records: dict[str, dict], trade_date: str, dry_run: bool = False) -> bool:
    """
    일일 리포트를 텔레그램으로 전송합니다.

    Args:
        records: {ticker: record} 딕셔너리
        trade_date: 거래일
        dry_run: True면 실제 전송하지 않고 로그만 출력

    Returns:
        성공 여부
    """
    message = format_daily_report(records, trade_date)

    if dry_run:
        logger.info(f"DRY-RUN 텔레그램 알림:\n{message}")
        return True

    return send_telegram(message)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== 텔레그램 알림 테스트 ===")
    test_records = {
        "TQQQ": {
            "closing_price": 50.0,
            "action": "buy_full",
            "buy_amount": 2500.0,
            "buy_shares": 50.0,
            "total_shares": 50.0,
            "avg_price": 50.0,
            "evaluation": 2500.0,
            "profit_ratio": 0.0,
            "cash_balance": 97500.0,
            "buy_count": 1,
            "cycle": 1,
        }
    }
    send_daily_report(test_records, "2026-03-18", dry_run=True)
