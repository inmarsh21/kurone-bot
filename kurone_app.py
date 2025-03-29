from flask import Flask, request, abort
from linebot.v3.messaging import MessagingApi, ApiClient, ReplyMessageRequest, TextMessage
from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

# LINEの認証情報
LINE_CHANNEL_ACCESS_TOKEN = "tIyCE/xxxxxx..."  # ←アクセストークンを実際のものに戻してね
LINE_CHANNEL_SECRET = "4dc62a09bfc7d5f785dbba1538a0483b"

# v3の正しい初期化方法（←ここがポイント）
client = ApiClient()
line_bot_api = MessagingApi(api_client=client)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def home():
    return "クロネBot最小構成、v3で起動中やで。"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print("🟡 Webhook受信:", body)

    try:
        handler.handle(body, signature)
        print("🟢 イベント処理成功")
    except InvalidSignatureError:
        print("❌ シグネチャエラー")
        abort(400)
    except Exception as e:
        print("💥 その他のエラー:", e)

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    print("📩 メッセージイベントきた！")
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text="クロネ：呼んだか？なんだお前かよ。")]
        )
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)

