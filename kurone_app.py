from flask import Flask, request, abort
import os
import random
from linebot.v3.messaging import (
    Configuration,
    MessagingApi,
    ApiClient,
    TextMessage,
    ReplyMessageRequest
)
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'tIyCE/XnhmCgdICOzqeU89R9MSi6j/AgbwaRGU+Dj4xlzDsw1sMJVC0MXL0X6dpOxid9jV2xU2OG1jVBpVCXTjEDKx44qH/yLLL8S4OWR6hsTYRqEusE/28rZSWntOuuROjtRo0H4N+XPj4mrIUoIQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '4dc62a09bfc7d5f785dbba1538a0483b'

config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
api_client = ApiClient(config)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

greeting_variants = [
    "呼んだか？…なんだ、お前かよ。",
    "オレが出るってことは、どうせヒマなんやろ。",
    "ったく…用事もないのに呼ぶなよな。",
    "……眠いんだけど。"
]

worry_keywords = ['つらい', 'しんどい', '不安', 'どうしよう', '疲れた', '最悪', '無理', '助けて', '泣きそう', 'うまくいかない']

@handler.add(MessageEvent)
def handle_message(event):
    if not isinstance(event.message, TextMessageContent):
        return

    user_message = event.message.text.strip()
    reply_text = ""

    # 占いワード
    fortune_keywords = ["占って", "占い", "うらない", "占", "占い頼む"]

    # ネガティブ系ワード
    worry_keywords = ['つらい', 'しんどい', '不安', 'どうしよう', '疲れた', '最悪', '無理', '助けて', '泣きそう', 'うまくいかない','嫌']

    # メッセージ分岐
    if any(keyword in user_message for keyword in fortune_keywords):
        # 占い対応
        reply_text = (
            "占いか。ったく、いちいち面倒くせぇな。\n"
            "でもどうせお前、気になってんだろ？\n"
            "ほら、何占うんだよ。\n"
            "【1】相性診断\n【2】タロット\n【3】ラッキーカラー\n"
            "番号でも単語でもさっさと言え。"
        )

    elif any(w in user_message for w in worry_keywords):
        # ネガティブ系対応（共感）
        reply_text = (
            "はぁ…お前、いきなり重てぇんだよ。\n"
            "全部どうでもよくなってんだろ？顔に書いてあるぞ。\n"
            "しょうがねぇから少しだけ相手してやる。感謝しろ。"
        )

    else:
        # それ以外は、雑に対応（greeting_variants から選択）
        reply_text = random.choice(greeting_variants)

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@app.route("/")
def home():
    return "クロネBotはv3で動作中やで！"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
