from flask import Flask, request, abort
import os
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

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent)
def handle_message(event):
    if not isinstance(event.message, TextMessageContent):
        return

    user_message = event.message.text.strip()
    reply_text = ""

    if user_message in ["こんにちは", "やあ", "よお", "ハロー"]:
        reply_text = "呼んだか？…なんだ、お前かよ。"
    elif "占って" in user_message:
        reply_text = (
            "しゃーねぇな。何を占えばいいんだよ？\n"
            "【1】相性診断\n【2】タロット\n【3】ラッキーカラー\n"
            "番号でも、名前でも言えや。"
        )
    else:
        reply_text = "…なんや、用がないなら呼ばんといてくれや。"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
    )
@app.route("/")
def home():
    return "クロネBotはv3で動作中やで！"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

