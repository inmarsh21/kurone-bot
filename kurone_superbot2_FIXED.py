# ==========================
# ① 会話ロジック（ユーザーとの対話・ステート管理）
# ==========================

user_states = {}
user_inputs = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip().lower()

    if user_id not in user_states:
        user_states[user_id] = "start"
        user_inputs[user_id] = {}

    state = user_states[user_id]

    # スタートワードに反応（セリフ強化）
    if msg in ["占って", "うらない", "start"]:
        user_states[user_id] = "choose_type"
        reply = (
            "クロネ：はぁ……またオレの出番かよ。"
            "しゃーねぇな。で、何を占えばいいんだ？"
            "【1】相性診断"
            "【2】タロット"
            "【3】ラッキーカラー"
            "番号でも、名前でもいいから言え。"
        )

    # 占いの種類を選ぶ（番号 or キーワード両対応 + セリフ演出）
    elif state == "choose_type":
            # ----- 💕 相性診断フロー -----
    elif state == "ask_name":
        user_inputs[user_id]["name"] = msg
        user_states[user_id] = "ask_birth_month"
        reply = "クロネ：誕生月は？（1〜12で答えろ）"

    elif state == "ask_birth_month":
        try:
            month = int(msg)
            if 1 <= month <= 12:
                user_inputs[user_id]["m1"] = month
                user_states[user_id] = "ask_birth_day"
                reply = "クロネ：で、何日生まれだよ？"
            else:
                reply = "クロネ：1〜12って言ってんだろ。ちゃんと月で答えろや。"
        except:
            reply = "クロネ：数字で月を言えっての。"

    elif state == "ask_birth_day":
        try:
            day = int(msg)
            if 1 <= day <= 31:
                user_inputs[user_id]["d1"] = day
                user_states[user_id] = "ask_partner_name"
                reply = "クロネ：気になってるヤツの名前は？"
            else:
                reply = "クロネ：1〜31の間で日を言え。常識な？"
        except:
            reply = "クロネ：数字で答えろよ、ったく。"

    elif state == "ask_partner_name":
        user_inputs[user_id]["partner"] = msg
        user_states[user_id] = "ask_partner_month"
        reply = "クロネ：そいつの誕生月は？"

    elif state == "ask_partner_month":
        try:
            month = int(msg)
            if 1 <= month <= 12:
                user_inputs[user_id]["m2"] = month
                user_states[user_id] = "ask_partner_day"
                reply = "クロネ：で、何日生まれだ？"
            else:
                reply = "クロネ：ちゃんと1〜12の月で言えや"
        except:
            reply = "クロネ：数字で頼むわ。そいつの月な。"

    elif state == "ask_partner_day":
        try:
            day = int(msg)
            if 1 <= day <= 31:
                user_inputs[user_id]["d2"] = day
                user_states[user_id] = "done"

                # 入力を取得して診断実行
                name = user_inputs[user_id]["name"]
                partner = user_inputs[user_id]["partner"]
                m1 = user_inputs[user_id]["m1"]
                d1 = user_inputs[user_id]["d1"]
                m2 = user_inputs[user_id]["m2"]
                d2 = user_inputs[user_id]["d2"]

                result = run_compatibility(user_id, m1, d1, m2, d2)
                reply = (
                    f"クロネ：ふーん…じゃ、診てやるよ\n\n"
                    f"🧑‍💼 {name}\n🎯 {partner}\n\n"
                    f"{result}\n\n"
                    "……満足したか？また占いたいなら『占って』って言えよ。"
                )
            else:
                reply = "クロネ：日付ってのは1〜31の間だろ？常識。"
        except:
            reply = "クロネ：数字ってわかるか？日付だ、日付。"

        if msg in ["1", "相性", "相性診断"]:
            user_states[user_id] = "ask_name"
            reply = (
                "クロネ：相性ぃ？ …知ってどうすんだよ。"
                "ま、いいけどな。"
                "まずはあんたの名前は？"
            )
        elif msg in ["2", "タロット", "tarot"]:
            user_states[user_id] = "tarot"
            reply = (
                "クロネ：タロットな…。"
                "オレの引きが冴えてるかどうか、試すってわけか。"
                + run_tarot_auto(user_id)
            )
        elif msg in ["3", "カラー", "ラッキーカラー", "色"]:
            user_states[user_id] = "lucky"
            reply = (
                "クロネ：色ぉ？ …そういうの気にするタイプかよ。"
                + run_lucky_color(user_id)
            )
        else:
            reply = (
                "クロネ：そんな占いはねぇよ。"
                "ちゃんと【1〜3】の番号か、占いの名前を言えっての。"
            )

    # ※ 他のステート（ask_name以降）は別途追記する

    else:
        reply = (
            "クロネ：……ったく、わかんねーなら最初から『占って』って言えよな。"
        )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


# ==========================
# ② 占いロジック本体（相性・タロット・ラッキーカラーなど）
# ==========================

# ----- 💕 相性診断 -----

def run_compatibility(user_id, m1, d1, m2, d2):
    # シンプルな相性スコア計算（誕生日の差をベースに）
    score = abs((m1 * 30 + d1) - (m2 * 30 + d2)) % 100
    score = 100 - score

    if score >= 90:
        comment = "😏 はいはい、相性バッチリ。いちゃいちゃしとけ"
    elif score >= 70:
        comment = "😌 まぁ悪くないな。でも油断すんなよ"
    elif score >= 50:
        comment = "😶 微妙ってやつだな。なんか合ってるようで合ってない"
    elif score >= 30:
        comment = "😬 ケンカばっかじゃねぇのか？"
    else:
        comment = "💀 無理。やめとけ"

    return f"相性スコア：{score}点\nクロネ：{comment}"



# ----- 🃏 タロット占い（3枚引き） -----

tarot_cards = [
    {"name": "愚者", "meaning": "自由・出発", "score": 2},
    {"name": "魔術師", "meaning": "創造・才能", "score": 2},
    {"name": "女教皇", "meaning": "知性・冷静", "score": 1},
    {"name": "女帝", "meaning": "豊かさ・母性", "score": 2},
    {"name": "皇帝", "meaning": "支配・行動力", "score": 2},
    {"name": "塔", "meaning": "崩壊・衝撃", "score": 0},
    {"name": "死神", "meaning": "終わり・再生", "score": 1},
    {"name": "太陽", "meaning": "成功・元気", "score": 3},
    {"name": "月", "meaning": "不安・幻想", "score": 1},
    {"name": "運命の輪", "meaning": "転機・幸運", "score": 3}
    # ※ 本来は22枚全て入れる（今回は10枚に絞ってます）
]

def run_tarot_auto(user_id):
    selected = random.sample(tarot_cards, 3)
    total_score = sum(c["score"] for c in selected)

    msg = "【タロット結果】\n"
    for i, card in enumerate(selected):
        pos = ["過去", "現在", "未来"][i]
        msg += f"◆ {pos}：『{card['name']}』 - {card['meaning']}\n"

    msg += f"\n🔮 総スコア：{total_score}/9\n"
    if total_score >= 8:
        msg += "クロネ：奇跡かよ…オレまで信じたくなるわ"
    elif total_score >= 5:
        msg += "クロネ：まぁ…普通？ってとこだな"
    else:
        msg += "クロネ：今日はやめとけ。まじで"

    return msg



# ----- 🌈 ラッキーカラー占い -----

lucky_colors = [
    {"color": "赤", "comment": ["情熱的になれる…といいな", "今日は前に出てみろ"]},
    {"color": "青", "comment": ["冷静になれる色、だといいな", "まあ、今日は青で気持ち沈めとけ"]},
    {"color": "黄", "comment": ["元気出すのにいいかもな", "明るいフリでもしとけ"]},
    {"color": "黒", "comment": ["オレかよ。まあ、落ち着いて行け", "黒は無難だな。何も起きねぇかも"]},
]

def run_lucky_color(user_id):
    lucky = random.choice(lucky_colors)
    comment = random.choice(lucky["comment"])
    return f"🌈 ラッキーカラーは『{lucky['color']}』\nクロネ：{comment}"


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
