"""
simulate_trade.py — 무한매수법 핵심 매매 로직

LOC 매수 판단, 평단가 계산, 익절/손절 판단, 사이클 리셋을 처리합니다.
"""

import json
import os
import logging
from datetime import datetime

# 프로젝트 루트를 기준으로 config 모듈 임포트
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    ALPHA, TAKE_PROFIT_RATIO, STOP_LOSS_RATIO,
    BUY_AMOUNT_PER_SPLIT, NUM_SPLITS, INITIAL_CAPITAL, STATE_FILE
)

logger = logging.getLogger(__name__)


def load_state() -> dict:
    """state.json에서 현재 포지션 상태를 로드합니다."""
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    """state.json에 포지션 상태를 저장합니다."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    logger.info("state.json 저장 완료")


def calculate_avg_price(position: dict) -> float:
    """평단가를 계산합니다. (총 매수금 / 총 보유수량)"""
    if position["total_shares"] == 0:
        return 0.0
    return position["total_cost"] / position["total_shares"]


def calculate_profit_ratio(position: dict, current_price: float) -> float:
    """현재 수익률을 계산합니다."""
    if position["total_cost"] == 0:
        return 0.0
    evaluation = position["total_shares"] * current_price
    return (evaluation - position["total_cost"]) / position["total_cost"]


def execute_buy(position: dict, price: float, amount: float) -> dict:
    """
    매수를 실행합니다.

    Args:
        position: 현재 포지션
        price: 매수 가격 (종가)
        amount: 매수 금액 (USD)

    Returns:
        업데이트된 포지션
    """
    if amount <= 0 or amount > position["cash_balance"]:
        amount = min(amount, position["cash_balance"])
        if amount <= 0:
            logger.warning("현금 잔고 부족 — 매수 불가")
            return position

    shares = amount / price
    position["total_shares"] = round(position["total_shares"] + shares, 6)
    position["total_cost"] = round(position["total_cost"] + amount, 2)
    position["cash_balance"] = round(position["cash_balance"] - amount, 2)
    position["buy_count"] += 1

    logger.info(
        f"  매수 체결: ${amount:.2f} → {shares:.4f}주 @ ${price:.2f} "
        f"(누적 {position['buy_count']}회)"
    )
    return position


def reset_cycle(position: dict, reason: str, current_price: float) -> dict:
    """
    사이클을 리셋합니다 (익절/손절 후).
    이전 사이클의 최종 평가금액을 다음 사이클의 원금으로 승계하여 누적합니다.

    Args:
        position: 현재 포지션
        reason: 리셋 사유 ("take_profit" 또는 "stop_loss")
        current_price: 현재 종가

    Returns:
        리셋된 포지션 (누적 자산 반영)
    """
    evaluation = position["total_shares"] * current_price
    # 새로운 시작 자산 = 현재 현금 잔고 + 주식 매도 대금(평가금)
    new_capital = round(position["cash_balance"] + evaluation, 2)
    
    profit = evaluation - position["total_cost"]
    profit_ratio = calculate_profit_ratio(position, current_price)

    logger.info(
        f"  {'🟢 익절' if reason == 'take_profit' else '🔴 손절'}! "
        f"평가금: ${evaluation:.2f}, 최종 회수액: ${new_capital:.2f}, 손익: ${profit:+.2f} ({profit_ratio:+.2%})"
    )

    # 사이클 리셋 및 자산 누적
    position["cycle"] += 1
    position["buy_count"] = 0
    position["total_shares"] = 0.0
    position["total_cost"] = 0.0
    position["initial_capital"] = new_capital
    position["cash_balance"] = new_capital
    position["status"] = "active"

    logger.info(f"  >>> 다음 사이클(#{position['cycle']}) 시작 자산: ${new_capital:.2f}")

    return position


def process_ticker(ticker: str, position: dict, closing_price: float, trade_date: str) -> dict:
    """
    한 종목에 대한 일일 매매 로직을 실행합니다.

    Args:
        ticker: 종목 코드
        position: 현재 포지션 상태
        closing_price: 당일 종가
        trade_date: 거래일 (YYYY-MM-DD)

    Returns:
        업데이트된 포지션 + 일일 기록 딕셔너리
    """
    logger.info(f"\n{'='*50}")
    logger.info(f"[{ticker}] {trade_date} 처리 시작 (사이클 #{position['cycle']})")
    logger.info(f"  종가: ${closing_price:.2f}")

    avg_price = calculate_avg_price(position)
    action = "hold"
    buy_amount = 0.0
    buy_shares = 0.0

    # ──────────────────────────────────────────────
    # 1. 익절/손절 판단 (매수 전에 먼저 체크)
    # ──────────────────────────────────────────────
    if position["total_shares"] > 0:
        profit_ratio = calculate_profit_ratio(position, closing_price)
        logger.info(f"  평단가: ${avg_price:.2f}, 수익률: {profit_ratio:+.2%}")

        if profit_ratio >= TAKE_PROFIT_RATIO:
            # 익절 기록 생성
            record = _create_record(
                trade_date, ticker, closing_price, position,
                action="take_profit", buy_amount=0, buy_shares=0
            )
            position = reset_cycle(position, "take_profit", closing_price)
            position["history"].append(record)
            return position

        if profit_ratio <= STOP_LOSS_RATIO:
            # 손절 기록 생성
            record = _create_record(
                trade_date, ticker, closing_price, position,
                action="stop_loss", buy_amount=0, buy_shares=0
            )
            position = reset_cycle(position, "stop_loss", closing_price)
            position["history"].append(record)
            return position

    # 1회 매수 금액 동적 계산 (현재 원금의 1/40)
    current_buy_amount = position["initial_capital"] / NUM_SPLITS

    # ──────────────────────────────────────────────
    # 2. 매수 로직 (LOC 방식)
    # ──────────────────────────────────────────────
    if position["buy_count"] >= NUM_SPLITS:
        logger.info(f"  {NUM_SPLITS}회 매수 완료 — 추가 매수 없이 대기")
        action = "wait"
    elif position["buy_count"] == 0:
        # 첫 매수 (T=1): 종가 기준 전액 매수
        buy_amount = min(current_buy_amount, position["cash_balance"])
        position = execute_buy(position, closing_price, buy_amount)
        buy_shares = buy_amount / closing_price
        action = "buy_full"
    elif closing_price <= avg_price:
        # 종가 ≤ 평단가: 전액 매수
        buy_amount = min(current_buy_amount, position["cash_balance"])
        position = execute_buy(position, closing_price, buy_amount)
        buy_shares = buy_amount / closing_price
        action = "buy_full"
    elif closing_price <= avg_price * (1 + ALPHA):
        # 평단가 < 종가 ≤ 평단가 × (1 + α): 절반 매수
        buy_amount = min(current_buy_amount / 2, position["cash_balance"])
        position = execute_buy(position, closing_price, buy_amount)
        buy_shares = buy_amount / closing_price
        action = "buy_half"
    else:
        # 종가 > 평단가 × (1 + α): 미체결
        logger.info(
            f"  미체결: 종가 ${closing_price:.2f} > "
            f"LOC 상한 ${avg_price * (1 + ALPHA):.2f}"
        )
        action = "no_fill"

    # ──────────────────────────────────────────────
    # 3. 기록 생성
    # ──────────────────────────────────────────────
    record = _create_record(
        trade_date, ticker, closing_price, position,
        action=action, buy_amount=buy_amount, buy_shares=buy_shares
    )
    position["history"].append(record)

    # 요약 로그
    new_avg = calculate_avg_price(position)
    new_profit = calculate_profit_ratio(position, closing_price)
    logger.info(
        f"  결과: 보유 {position['total_shares']:.4f}주, "
        f"평단가 ${new_avg:.2f}, 수익률 {new_profit:+.2%}, "
        f"현금잔고 ${position['cash_balance']:.2f}"
    )

    return position


def _create_record(
    trade_date: str, ticker: str, closing_price: float,
    position: dict, action: str, buy_amount: float, buy_shares: float
) -> dict:
    """일일 매매 기록을 생성합니다."""
    avg_price = calculate_avg_price(position)
    evaluation = position["total_shares"] * closing_price
    profit_ratio = calculate_profit_ratio(position, closing_price)

    return {
        "date": trade_date,
        "ticker": ticker,
        "closing_price": round(closing_price, 4),
        "action": action,
        "buy_amount": round(buy_amount, 2),
        "buy_shares": round(buy_shares, 6),
        "total_shares": round(position["total_shares"], 6),
        "total_cost": round(position["total_cost"], 2),
        "avg_price": round(avg_price, 4),
        "evaluation": round(evaluation, 2),
        "profit_ratio": round(profit_ratio, 6),
        "cash_balance": round(position["cash_balance"], 2),
        "buy_count": position["buy_count"],
        "cycle": position["cycle"],
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== 매매 로직 테스트 ===")
    state = load_state()
    # 테스트용 가상 종가
    test_price = 50.0
    for ticker in ["TQQQ", "SOLX"]:
        state[ticker] = process_ticker(ticker, state[ticker], test_price, "2026-03-18")
    save_state(state)
    print("테스트 완료. state.json을 확인하세요.")
