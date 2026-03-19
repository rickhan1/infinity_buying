import json
import random
import os
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "state.json")

INTROS = [
    "안녕하세요! 기계처럼 매수하는 무한매수법 봇입니다.",
    "감정을 배제하고 기계적으로 투자하는 인피니티 바잉 시뮬레이터입니다.",
    "오늘도 미국 주식 시장이 마감되었습니다! 무한매수법 성과를 살펴볼까요?"
]

OUTROS = [
    "과연 이 기계적인 투자의 끝은 익절일까요? 다음 영상이 궁금하시다면 구독과 좋아요 부탁드립니다!",
    "매일 매일 투명하게 공개되는 무한매수법 시뮬레이터! 구독하시고 결과를 지켜봐주세요.",
    "하락장 방어에 특화된 무한매수법! 내일도 성과 리포트로 돌아오겠습니다."
]

ACTION_MAP = {
    "buy_full": "전액 매수",
    "buy_half": "절반 매수",
    "unfilled": "매수 미체결 (조건 미달)",
    "sell_profit": "목표 수익 도달로 전량 익절",
    "sell_loss": "손절 라인 도달로 전량 손절"
}

def generate_script():
    if not os.path.exists(STATE_FILE):
        return "데이터가 아직 없습니다."

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    intro = random.choice(INTROS)
    outro = random.choice(OUTROS)
    
    tqqq = state.get("TQQQ", {})
    solx = state.get("SOLX", {})
    
    tqqq_hist = tqqq.get("history", [])
    if not tqqq_hist:
        return intro + " 아직 매매 기록이 존재하지 않습니다. 첫 거래일을 기다려주세요! " + outro

    latest_record = tqqq_hist[-1]
    trade_date = latest_record.get("date", datetime.today().strftime('%Y-%m-%d'))
    
    # Body Generation
    body_lines = [f"오늘 {trade_date}의 매매 결과를 보고 드립니다."]
    
    for ticker, data in [("TQQQ", tqqq), ("SOLX", solx)]:
        hist = data.get("history", [])
        if not hist: continue
        today_data = hist[-1]
        
        action_kr = ACTION_MAP.get(today_data["action"], today_data["action"])
        cycle = today_data["cycle"]
        buy_count = today_data["buy_count"]
        profit_ratio = today_data["profit_ratio"] * 100
        
        body_lines.append(f"먼저 {ticker}입니다.")
        body_lines.append(f"현재 시즌 {cycle}의 {buy_count}회차 진행 중이며, 종가는 {today_data['closing_price']}달러를 기록했습니다.")
        body_lines.append(f"오늘의 액션은 '{action_kr}' 이었습니다.")
        
        if profit_ratio > 0:
            body_lines.append(f"현재 총 수익률은 플러스 {profit_ratio:.2f} 퍼센트로 수익권에 진입했습니다!")
        elif profit_ratio < 0:
            body_lines.append(f"현재 총 수익률은 마이너스 {abs(profit_ratio):.2f} 퍼센트입니다. 꾸준히 평단가를 낮춰가고 있습니다.")
        else:
            body_lines.append(f"현재 총 수익률은 0퍼센트입니다.")

    body = " ".join(body_lines)
    script = f"{intro} {body} {outro}"
    
    print(f"[Generated Script]\n{script}\n")
    return script, trade_date

if __name__ == "__main__":
    generate_script()
