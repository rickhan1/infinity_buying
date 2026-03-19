import json
import os
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "state.json")

def evaluate_profit_ko(profit_ratio, cycle, buy_count):
    if profit_ratio >= 10.0: return f"수익률 {profit_ratio:.2f}% 익절 도달! 시즌 {cycle+1}을 새로 시작합니다."
    elif profit_ratio <= -10.0: return f"마이너스 10% 위험 도달로 기계적 손절 후, 시즌 {cycle+1} 재개합니다."
    elif profit_ratio > 0: return f"총 수익률 {profit_ratio:.2f}%로 순항 중입니다. 익절을 기다립니다."
    return f"현재 {profit_ratio:.2f}% 하락 구간. 원칙대로 평단가를 낮추며 비중을 싣습니다."

def evaluate_profit_en(profit_ratio, cycle, buy_count):
    if profit_ratio >= 10.0: return f"Hit {profit_ratio:.2f}% profit! Full Take-Profit. Starting Season {cycle+1} now."
    elif profit_ratio <= -10.0: return f"Hit -10% stop-loss. Resetting mechanically for Season {cycle+1}."
    elif profit_ratio > 0: return f"Cruising at {profit_ratio:.2f}% profit. Waiting for target."
    return f"Currently at {profit_ratio:.2f}%. We mechanically buy the dip to lower average cost."

def generate_scripts():
    if not os.path.exists(STATE_FILE):
        return None, None, None

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    # 기본값
    tqqq = state.get("TQQQ", {})
    solx = state.get("SOLX", {})
    trade_date = datetime.today().strftime('%Y-%m-%d')
    if "history" in tqqq and tqqq["history"]:
        trade_date = tqqq["history"][-1]["date"]

    # 1. KOREAN SCRIPT
    intro_ko = f"무한매수 봇, {trade_date} 마감 보고입니다. "
    
    tqqq_ko = ""
    if "history" in tqqq and tqqq["history"]:
        td = tqqq["history"][-1]
        tqqq_ko += f"TQQQ 차트와 잔고입니다. 종가 {td['closing_price']}달러. "
        if td["action"] == "buy_full": tqqq_ko += "평단가 아래라 100% 매수 체결했습니다. "
        elif td["action"] == "buy_half": tqqq_ko += "수익권이라 50% 절반 매수했습니다. "
        tqqq_ko += evaluate_profit_ko(td["profit_ratio"] * 100, td["cycle"], td["buy_count"])
        tqqq_ko += " TQQQ 상세 히스토리입니다. "

    solx_ko = ""
    if "history" in solx and solx["history"]:
        sd = solx["history"][-1]
        solx_ko += f"다음 SOLX 차트입니다. 종가 {sd['closing_price']}달러. "
        if sd["action"] == "buy_full": solx_ko += "시그널 점에 맞춰 통쾌하게 100% 매수했습니다. "
        elif sd["action"] == "buy_half": solx_ko += "안전하게 50% 절반 매수입니다. "
        solx_ko += evaluate_profit_ko(sd["profit_ratio"] * 100, sd["cycle"], sd["buy_count"])
        solx_ko += " SOLX 상세 히스토리입니다. "
        
    outro_ko = "기계는 하락장에 떨지 않습니다. 내일 결과가 궁금하면 구독하시고, 여러분의 투자 생각도 댓글로 자유롭게 남겨주세요!"
    script_ko = f"{intro_ko} {tqqq_ko} {solx_ko} {outro_ko}"

    # 2. ENGLISH SCRIPT
    intro_en = f"Infinity Bot, market report for {trade_date}. "
    
    tqqq_en = ""
    if "history" in tqqq and tqqq["history"]:
        td = tqqq["history"][-1]
        tqqq_en += f"TQQQ chart. Close price {td['closing_price']} dollars. "
        if td["action"] == "buy_full": tqqq_en += "Below average, executed 100% Full Buy. "
        elif td["action"] == "buy_half": tqqq_en += "In profit, executed 50% Half Buy. "
        tqqq_en += evaluate_profit_en(td["profit_ratio"] * 100, td["cycle"], td["buy_count"])
        tqqq_en += " TQQQ specific transaction history. "

    solx_en = ""
    if "history" in solx and solx["history"]:
        sd = solx["history"][-1]
        solx_en += f"Next, SOLX chart. Close price {sd['closing_price']} dollars. "
        if sd["action"] == "buy_full": solx_en += "Bought 100% full capacity on dip. "
        elif sd["action"] == "buy_half": solx_en += "Conservative 50% half buy executed. "
        solx_en += evaluate_profit_en(sd["profit_ratio"] * 100, sd["cycle"], sd["buy_count"])
        solx_en += " SOLX detailed transaction history. "
        
    outro_en = "Bots don't panic. Subscribe for tomorrow's cold hard results, and drop your thoughts in the comments!"
    script_en = f"{intro_en} {tqqq_en} {solx_en} {outro_en}"

    print(f"✅ 한국어/영어 쇼츠 분석 대본 생성 렌더링 완료!")
    return script_ko, script_en, trade_date

if __name__ == "__main__":
    k, e, d = generate_scripts()
    print("KO:", k)
    print("EN:", e)
