from flask import Flask, request, abort
import os
import random

from linebot.v3.messaging import (
    MessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage
)

from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.exceptions import InvalidSignatureError

# Flaskアプリ初期化
app = Flask(__name__)

# LINE APIの認証情報
LINE_CHANNEL_ACCESS_TOKEN = 'Hkx9c2oPZcxHPWVJ0NwAKYcby9aZ92mflJh/tH+WUPBDMJkqchr0oheJuGEvC7NHxid9jV2xU2OG1jVBpVCXTjEDKx44qH/yLLL8S4OWR6hx4cbF/k3ExRwIVtZdUY8rNN5zSKSlx50RKDkOwhgvPAdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '4dc62a09bfc7d5f785dbba1538a0483b'

# LINE Bot SDK v3 初期化
config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line_bot_api = MessagingApi(config)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

user_states = {}

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print("🟡 受信したbody:", body)

    try:
        handler.handle(body, signature)
        print("🟢 handler.handle() 成功！")
    except InvalidSignatureError:
        print("❌ シグネチャエラー：Token/Secret違いかも")
        abort(400)
    except Exception as e:
        print("💥 その他のエラー:", e)

    return "OK"

@app.route("/")
def home():
    return "クロネ占いBotはv3で動作中やで。LINEから『占って』って送ってな！"

@handler.add(MessageEvent)
def debug_handler(event):
    if isinstance(event.message, TextMessageContent):
        user_id = event.source.user_id
        msg = event.message.text
        print("📩 イベントきたで！")
        print("🧾 ユーザーID:", user_id)
        print("🧾 メッセージ内容:", msg)

        # 簡単な返信テスト（ここから機能を拡張可能）
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="クロネ：はいはい、来たで")]
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting app on port {port}")
    app.run(host="0.0.0.0", port=port)
