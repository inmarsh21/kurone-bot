# ==========================
# ① 会話ロジック（ユーザーとの対話・ステート管理）
# ==========================

user_states = {}
user_inputs = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    if user_id not in user_states:
        user_states[user_id] = "start"
        user_inputs[user_id] = {}

    state = user_states[user_id]

    if msg.lower() in ["占って", "うらない", "start"]:
        user_states[user_id] = "choose_type"
        reply = "クロネ：はぁ……何を占えばいいんだよ？\n1. 相性\n2. タロット\n3. ラッキーカラー"

    elif state == "choose_type":
        if "1" in msg:
            user_states[user_id] = "ask_name"
            reply = "クロネ：相性ぃ？ ま、いいけどな。まずあんたの名前は？"
        elif "2" in msg:
            user_states[user_id] = "tarot"
            reply = run_tarot_auto(user_id)
        elif "3" in msg:
            user_states[user_id] = "lucky"
            reply = run_lucky_color(user_id)
        else:
            reply = "クロネ：選択肢ちゃんと見てんのか？\n1〜3で答えろよ"
    else:
        reply = "クロネ：占ってって言えってば"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


# ==========================
# ② 占いロジック本体（相性・タロット・ラッキーカラーなど）
# ==========================

def run_tarot_auto(user_id):
    return "[タロット結果] ※ここに実装してね"

def run_lucky_color(user_id):
    return "[ラッキーカラー結果] ※ここに実装してね"


# ==========================
# ③ 感情・セリフ演出（毒舌・やさしさ・あきれ・皮肉など）
# ==========================

emotion_patterns = {
    "neutral": ["ふーん", "まぁな", "どうでもいいけどな"],
    "sarcastic": ["笑わせんなよ", "それ本気で言ってんのか？", "やれやれ"],
    "encouraging": ["……頑張れよ、ちょっとだけな", "オレでも応援する時あるぞ"],
}


# ==========================
# ④ 定数・設定エリア（カード・色・演出の素材群）
# ==========================

tarot_cards = [
    {"name": "愚者", "meaning": "自由、冒険", "score": 3},
    # ... 他カード追加
]

lucky_colors = [
    {"color": "赤", "comment": ["今日の赤はちょっとアツいかもな"]},
    # ... 他の色
]


# ==========================
# ⑤ ユーティリティ関数（共通処理・日付変換・整形など）
# ==========================

def format_tarot_result(card):
    return f"【{card['name']}】
意味：{card['meaning']}"

def log_state(user_id, state):
    print(f"[LOG] {user_id} → 状態：{state}")

def get_today_str():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


# ==========================
# ⑥ ログ・デバッグ表示（ステート確認など）
# ==========================

# 開発中はここにログ出力、RenderのLogsで確認しやすく
# 本番時はコメントアウトOK

# log_state(user_id, user_states[user_id])


# ==========================
# ⑦ 外部連携用スペース（DB接続・履歴保存など）
# ==========================

# 例：Firebaseやファイル保存など導入する場合はここに追記

# def save_result_to_db(user_id, result):
#     pass  # TODO: 実装予定


# ==========================
# 🧩 Flask + LINE Webhook連携
# ==========================

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import random

app = Flask(__name__)
LINE_CHANNEL_ACCESS_TOKEN = 'Hkx9c2oPZcxHPWVJ0NwAKYcby9aZ92mflJh/tH+WUPBDMJkqchr0oheJuGEvC7NHxid9jV2xU2OG1jVBpVCXTjEDKx44qH/yLLL8S4OWR6hx4cbF/k3ExRwIVtZdUY8rNN5zSKSlx50RKDkOwhgvPAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '4dc62a09bfc7d5f785dbba1538a0483b'
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
