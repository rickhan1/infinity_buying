"""
fetch_stock_data.py — 주가 데이터 수집 모듈

yfinance를 사용하여 TQQQ, SOLX의 당일 종가 데이터를 수집합니다.
주말/공휴일(비거래일)인 경우를 감지합니다.
"""

import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def get_closing_prices(tickers: list[str], date: str | None = None) -> dict[str, float | None]:
    """
    지정된 종목들의 종가를 수집합니다.

    Args:
        tickers: 종목 코드 리스트 (예: ["TQQQ", "SOLX"])
        date: 조회 날짜 (YYYY-MM-DD). None이면 가장 최근 거래일.

    Returns:
        {ticker: closing_price} 딕셔너리.
        거래일이 아니거나 데이터가 없으면 해당 종목의 값은 None.
    """
    results = {}

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)

            if date:
                # 특정 날짜의 종가 조회
                target_date = datetime.strptime(date, "%Y-%m-%d")
                start = target_date.strftime("%Y-%m-%d")
                end = (target_date + timedelta(days=1)).strftime("%Y-%m-%d")
                hist = stock.history(start=start, end=end)
            else:
                # 가장 최근 거래일 종가 조회
                hist = stock.history(period="1d")

            if hist.empty:
                logger.warning(f"[{ticker}] 데이터 없음 (비거래일 가능성)")
                results[ticker] = None
            else:
                close_price = round(float(hist["Close"].iloc[-1]), 4)
                trade_date = hist.index[-1].strftime("%Y-%m-%d")
                logger.info(f"[{ticker}] {trade_date} 종가: ${close_price}")
                results[ticker] = close_price

        except Exception as e:
            logger.error(f"[{ticker}] 데이터 수집 실패: {e}")
            results[ticker] = None

    return results


def get_latest_trade_date(ticker: str = "TQQQ") -> str | None:
    """
    가장 최근 거래일 날짜를 반환합니다.

    Returns:
        최근 거래일 (YYYY-MM-DD) 또는 None
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            return hist.index[-1].strftime("%Y-%m-%d")
    except Exception as e:
        logger.error(f"최근 거래일 조회 실패: {e}")
    return None


def is_trading_day(date: str | None = None) -> bool:
    """
    해당 날짜가 거래일인지 확인합니다.

    Args:
        date: 확인할 날짜 (YYYY-MM-DD). None이면 오늘.

    Returns:
        거래일이면 True
    """
    prices = get_closing_prices(["TQQQ"], date)
    return prices.get("TQQQ") is not None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("=== 주가 데이터 수집 테스트 ===")
    print(f"최근 거래일: {get_latest_trade_date()}")
    prices = get_closing_prices(["TQQQ", "SOLX"])
    for ticker, price in prices.items():
        if price:
            print(f"  {ticker}: ${price}")
        else:
            print(f"  {ticker}: 데이터 없음")
