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