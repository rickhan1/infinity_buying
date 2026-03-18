import os
import json
from flask import Flask, jsonify
from flask_cors import CORS

from config import STATE_FILE

app = Flask(__name__)
# 로컬 프론트엔드(Vite)에서 접근할 수 있도록 CORS 허용
CORS(app)

@app.route('/api/state', methods=['GET'])
def get_state():
    """
    state.json 파일을 읽어서 그대로 반환합니다.
    (내부에 요약 데이터와 전 종목 전체 History 리스트가 이미 모두 포함되어 있습니다)
    """
    if not os.path.exists(STATE_FILE):
        return jsonify({"error": "State file not found."}), 404
        
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 데브 서버 실행 (macOS AirPlay 충돌 방지용 5001)
    app.run(host='0.0.0.0', port=5001, debug=True)
