from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi, Configuration, ReplyMessageRequest, TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

# LINEの認証情報（実際は環境変数が推奨）
LINE_CHANNEL_ACCESS_TOKEN = "tIyCE/XnhmCgdICOzqeU89R9MSi6j/AgbwaRGU+Dj4xlzDsw1sMJVC0MXL0X6dpOxid9jV2xU2OG1jVBpVCXTjEDKx44qH/yLLL8S4OWR6hsTYRqEusE/28rZSWntOuuROjtRo0H4N+XPj4mrIUoIQdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "4dc62a09bfc7d5f785dbba1538a0483b"

# LINE API 初期化（v3）
config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line_bot_api = MessagingApi(config)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def home():
    return "クロネ占いBotは起動中やで！"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print("🔔 Webhook受信:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent)
def handle_message(event):
    if hasattr(event.message, "text"):
        user_text = event.message.text
        print("💬 ユーザー:", user_text)

        reply = "クロネ：ほーん、それで？"
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)
