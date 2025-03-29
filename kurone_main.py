<<<<<<< HEAD
# ==========================
# 🧩 Flask + LINE Webhook連携
# ==========================

from flask import Flask, request, abort
import os
import random

from linebot.v3.messaging import (
    MessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage  # ←これ追加！
)

from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent
from linebot.exceptions import InvalidSignatureError
from linebot.v3.messaging import MessagingApiClient

app = Flask(__name__)
app = Flask(__name__)

# LINE APIの認証情報（セキュリティ的には環境変数推奨）
LINE_CHANNEL_ACCESS_TOKEN = 'tIyCE/XnhmCgdICOzqeU89R9MSi6j/AgbwaRGU+Dj4xlzDsw1sMJVC0MXL0X6dpOxid9jV2xU2OG1jVBpVCXTjEDKx44qH/yLLL8S4OWR6hsTYRqEusE/28rZSWntOuuROjtRo0H4N+XPj4mrIUoIQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '4dc62a09bfc7d5f785dbba1538a0483b'

# v3対応LINE Bot初期化
line_bot_api = MessagingApiClient(LINE_CHANNEL_ACCESS_TOKEN)
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

# ==========================
# ① 会話ロジック（ユーザーとの対話・ステート管理）
# ==========================

user_states = {}
user_inputs = {}



@handler.add(MessageEvent)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text
    state = user_states.get(user_id, "start")
    reply = ""

    if "占い" in msg:
        flex_contents = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "占い結果をここに表示"}
                ]
            }
        }
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[FlexMessage(alt_text="占い結果", contents=flex_contents)]
            )
        )
        return

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

    elif state == "choose_type":
        if msg in ["1", "相性", "相性診断"]:
            user_states[user_id] = "ask_name"
            reply = "クロネ：相性ぃ？ …知ってどうすんだよ。ま、いいけどな。まずはあんたの名前は？"
        elif msg in ["2", "タロット", "tarot"]:
            user_states[user_id] = "tarot"
            reply = "クロネ：タロットな…。オレの引きが冴えてるかどうか、試すってわけか。\n" + kurone_tarot_reading()
        elif msg in ["3", "カラー", "ラッキーカラー", "色"]:
            user_states[user_id] = "lucky"
            reply = "クロネ：色ぉ？ …そういうの気にするタイプかよ。" + run_lucky_color(user_id)
        else:
            reply = "クロネ：そんな占いはねぇよ。ちゃんと【1〜3】の番号か、占いの名前を言えっての。"

    elif state == "ask_name":
        if user_id not in user_inputs:
            user_inputs[user_id] = {}
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
        except ValueError:
            reply = "クロネ：数字で月を言えっての。"

    elif state == "ask_birth_day":
        try:
            day = int(msg)
            if 1 <= day <= 31:
                user_inputs[user_id]["d1"] = day
                user_states[user_id] = "ask_partner_name"
                reply = "クロネ：気になってるヤツの名前は？"
            else:
                reply = "クロネ：1〜31の間で言え。常識な？"
        except ValueError:
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
        except ValueError:
            reply = "クロネ：数字で頼むわ。そいつの月な。"

    elif state == "ask_partner_day":
        try:
            day = int(msg)
            if 1 <= day <= 31:
                user_inputs[user_id]["d2"] = day
                user_states[user_id] = "done"
                name = user_inputs[user_id]["name"]
                partner = user_inputs[user_id]["partner"]
                m1 = user_inputs[user_id]["m1"]
                d1 = user_inputs[user_id]["d1"]
                m2 = user_inputs[user_id]["m2"]
                d2 = user_inputs[user_id]["d2"]
                result = run_compatibility(user_id, m1, d1, m2, d2)
                reply = (
                    f"クロネ：ふーん…じゃ、診てやるよ"
                    f"🧑‍💼 {name}🎯 {partner}"
                    f"{result}"
                    "……満足したか？また占いたいなら『占って』って言えよ。"
                )
            else:
                reply = "クロネ：日付ってのは1〜31の間だろ？常識。"
        except ValueError:
            reply = "クロネ：数字ってわかるか？日付だ、日付。"

    else:
        reply = "クロネ：……ったく、わかんねーなら最初から『占って』って言えよな。"

    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


    # ※ 他のステート（ask_name以降）は別途追記する





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


# ----- 🃏 タロットセリフ辞書（tarot_kurone_lines） -----
tarot_kurone_lines = {
    "愚者": {
        "過去": "なーんも考えんと突っ走ったツケ、今頃出とるだけやろ…",
        "現在": "はぁ…自由に見えて、ただの現実逃避ってこと、気づいてへんやろ",
        "未来": "落ちるとこまで落ちて、ようやく地に足つくかもな。でも、それも悪くない…かもな"
    },
    "魔術師": {
        "過去": "器用貧乏やったんちゃう？なんでも手出して、なんもモノになってへん",
        "現在": "始めるのはええけど、中身スカスカやったら意味ないで",
        "未来": "もし今の努力が実を結ぶなら…奇跡やな。でも、ないとは言わへんで"
    },
    "女教皇": {
        "過去": "分かったふりして距離置いてたやろ？ほんまは何も見えてなかったんちゃうか",
        "現在": "静かにしてたら正解が降ってくると思うてるん？甘いで",
        "未来": "本物の直感ってやつが出てくるかもな…それ、信じられたらの話やけど"
    },
    "女帝": {
        "過去": "甘やかされた結果が今のぬるい自分ちゃう？",
        "現在": "与えるとか包み込むとか…あんたにその余裕、あるんか？",
        "未来": "もし今、誰かをちゃんと大事にできるなら…それは誇ってええかもしれんな"
    },
    "皇帝": {
        "過去": "力でねじ伏せようとして、結局孤独になっただけやろ",
        "現在": "威厳とか言う前に、自分の不安隠すのやめたらどうや？",
        "未来": "もし誰かに背中見せられる日が来るなら…その時はちゃんと立て、絶対に"
    },
    "教皇": {
        "過去": "人の言うことばっか聞いて、自分の声無視してたんちゃう？",
        "現在": "教えとかルールって、時には毒になるねん。気づけや",
        "未来": "正しさに守られるんじゃなく、正しさを選べるなら…その時はちょっと、希望あるかもな"
    },
    "恋人": {
        "過去": "選ばれへんかったんは、お前のせいやろ",
        "現在": "自分の気持ちすらわからんのに、他人と向き合えるわけないやん",
        "未来": "もし本当に選ぶ覚悟ができたら…今度こそ、手放さずにすむかもな"
    },
    "戦車": {
        "過去": "突っ走ったはええけど、心はどっかに置いてきたんちゃう？",
        "現在": "勝ちたくて必死なんやろ？でも、何に勝つつもりやねん",
        "未来": "もし本気で進む覚悟があるなら…勝ち方も見えてくるかもな。オレも…ちょっと応援するわ"
    },
    "力": {
        "過去": "抑え込んでただけで、なんも克服できてへんやん",
        "現在": "強がってんの、バレバレやで",
        "未来": "ほんまの強さってのを見せてくれるんやったら…オレ、見届けてもええわ"
    },
    "隠者": {
        "過去": "逃げただけやん。ひとりになるのが楽やっただけやろ",
        "現在": "ほんまは誰かに気づいてほしいくせに、殻にこもってるとかダサいで",
        "未来": "その孤独が、いつか光に変わるなら…悪い未来やないな"
    },
    "運命の輪": {
        "過去": "チャンスやったかもしれへんけど、結局流されて終わりやったんちゃう",
        "現在": "運に頼るしかないって状況、もう詰んどるやん",
        "未来": "でもな、運命ってやつが味方してくれる瞬間も…たまにある。信じるかどうかはお前次第や"
    },
    "正義": {
        "過去": "バランス取ったつもりが、誰かに犠牲押し付けただけちゃう？",
        "現在": "自分が正しいって思いたいだけやろ。ほんまは揺らいでんのに",
        "未来": "もし本当に自分と向き合えるなら、ちょっとは救われるんかもな"
    },
    "吊るされた男": {
        "過去": "我慢したフリして、何も変える気なかっただけやろ",
        "現在": "動けへん言い訳して、自分から止まってんの気づいてる？",
        "未来": "それでも見方を変えたら…世界が少しマシに見えるかもな"
    },
    "死神": {
        "過去": "終わったのに、まだ引きずってるんアホらし",
        "現在": "変わるチャンス来とるのに、ビビって何もしてへんやん",
        "未来": "終わるからこそ始まるんや。…ま、終われたらの話やけどな"
    },
    "節制": {
        "過去": "どっちつかずで中途半端…そりゃ何も残らんわな",
        "現在": "うまくやろうとして、結局何にもできてへんやん",
        "未来": "ほんまの調和が訪れるなら…そろそろブレるのやめえや"
    },
    "悪魔": {
        "過去": "欲望に飲まれて、自分でも気づかんうちに腐っとったんちゃう？",
        "現在": "依存に気づかへんふりしてるけど、もう手遅れかもな",
        "未来": "でも、もしその鎖を自分で切れたら…ちょっとはマシな未来あるで"
    },
    "塔": {
        "過去": "全部崩れたんは、お前が見て見ぬふりしとったからやろ",
        "現在": "あーあ、今まさに崩れてるとこやん。どうすんのこれ？",
        "未来": "ゼロからでも、建て直せる力があるなら…まだ終わりやないな"
    },
    "星": {
        "過去": "希望持ったフリして、何にもしてへんかったんちゃう？",
        "現在": "理想語るのはええけど、現実見えてへんやろ",
        "未来": "…それでも、その光を信じたいって思えるなら、ええ夢かもな"
    },
    "月": {
        "過去": "不安に流されて、現実も夢もぐちゃぐちゃやったやろ",
        "現在": "目の前のこと、ほんまに見えてるんか？全部幻ちゃうんか",
        "未来": "それでも迷いながら進めるなら…ちょっとは価値あるかもしれんな"
    },
    "太陽": {
        "過去": "楽しそうに見えて、結局見栄やっただけちゃう？",
        "現在": "幸せそうやけど…それ、ホンマに本心か？演じてへん？",
        "未来": "…でもな、今度こそ心から笑えるなら、それは…羨ましいかもな"
    },
    "審判": {
        "過去": "後悔ばっかで、何ひとつ清算できてへんやん",
        "現在": "過去に引きずられて、今を捨てるとかアホすぎやろ",
        "未来": "ほんまに向き合えたら、生まれ変われるかもしれへんな…一応、な"
    },
    "世界": {
        "過去": "完璧求めすぎて、自分でも疲れとったんちゃう？",
        "現在": "今が完成形とか思ってへんよな？ただの終わりに見えるで",
        "未来": "それでも、ほんまに全うできたなら…オレ、ちょっとだけ認めたるわ"
    }
}

# ----- 🃏 タロット占い（3枚引き） -----

tarot_scores = {
    # 🌟 超吉（+3）
    "太陽": 3,
    "世界": 3,
    "星": 3,

    # 👍 吉（+2）
    "恋人": 2,
    "戦車": 2,
    "審判": 2,

    # 🙂 小吉（+1）
    "力": 1,
    "皇帝": 1,
    "節制": 1,

    # 😐 平（0）
    "魔術師": 0,
    "正義": 0,
    "教皇": 0,
    "愚者": 0,

    # 🙁 小凶（-1）
    "女教皇": -1,
    "隠者": -1,
    "月": -1,
    "吊るされた男": -1,

    # 😖 凶（-2）
    "死神": -2,
    "悪魔": -2,

    # 💀 大凶（-3）
    "塔": -3
}

# ----- 🃏 タロット占い（3枚引き） -----
def kurone_tarot_reading():

    
    cards = list(tarot_kurone_lines.keys())
    selected = random.sample(cards, 3)
    positions = ["過去", "現在", "未来"]

    intro = "🐾 カサカサ…クロネが無言でカードを3枚並べた。\n"
    intro += "💭「ったく、こんなもん占ってどうすんだよ……」\n"
    intro += "でも…少しだけ本気になったようだ。\n"

    result = "🔮 【タロット3枚引き】\n" + intro

    total_score = 0

    for i in range(3):
        card = selected[i]
        pos = positions[i]
        line = tarot_kurone_lines[card][pos]
        score = tarot_scores.get(card, 0)
        total_score += score
        result += f"\n━━━\n【{pos}】🃏{card}（{score:+d}）\n💭クロネ「{line}」\n"

    # 💯 スコア評価コメント
    if total_score >= 6:
        comment = "…オレが言うのもアレやけど、運命の寵児ちゃうか？"
    elif total_score >= 3:
        comment = "お前にしては…まぁ上出来やな"
    elif total_score >= 1:
        comment = "まぁ…悪くはないんちゃう？"
    elif total_score >= -1:
        comment = "うーん、微妙やな"
    elif total_score >= -4:
        comment = "正直、調子悪そやな"
    else:
        comment = "……今日は寝とけ"

    result += f"\n━━━\n💯 総合スコア：{total_score:+d}（{comment}）"

    return result


def create_tarot_flex():
    cards = list(tarot_kurone_lines.keys())
    selected = random.sample(cards, 3)
    positions = ["過去", "現在", "未来"]
    bubbles = []

    for i in range(3):
        card = selected[i]
        pos = positions[i]
        line = tarot_kurone_lines[card][pos]
        score = tarot_scores.get(card, 0)

        bubble = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": f"【{pos}】🃏{card}", "weight": "bold", "size": "lg"},
                    {"type": "text", "text": f"スコア：{score:+d}", "size": "sm", "color": "#999999"},
                    {"type": "box", "layout": "horizontal", "contents": [
                        {"type": "text", "text": f"💭 クロネ「{line}」", "wrap": True, "size": "sm"}
                    ]}
                ]
            }
        }
        bubbles.append(bubble)

    # 複数バブルをcarousel形式で返す
    flex = {
        "type": "carousel",
        "contents": bubbles
    }

    return FlexMessage(alt_text="クロネのタロット占い結果", contents=flex)

# ----- 🌈 ラッキーカラー占い -----
lucky_colors = [
    {
        "color": "赤",
        "emotion": ["今日は燃えてるな…気合だけは認めてやる", "アツくなりすぎて空回りすんなよ"],
        "trend": "行動力と情熱が高まりやすい日。",
        "advice": "言いたいことはちゃんと口に出せ。ただしケンカ腰はやめとけ。"
    },
    {
        "color": "青",
        "emotion": ["冷静？オレには無理だな。あんたは頑張れ", "心、落ち着かせとけ。うるさいの苦手だから"],
        "trend": "判断力が増して集中しやすい。",
        "advice": "静かな場所で考え事するといいかもな。人の話はよく聞けよ。"
    },
    {
        "color": "黄",
        "emotion": ["元気に見せとけば何とかなる…かもな", "明るく振る舞うのって、けっこう疲れるんだぞ？"],
        "trend": "好奇心と社交性が高まる日。",
        "advice": "人と話すのも悪くない。ただし無理すんなよ。"
    },
    {
        "color": "緑",
        "emotion": ["穏やか？…らしくねぇけど今日はそれでいい", "のんびりしすぎて腐るなよ"],
        "trend": "バランス感覚と癒しがテーマ。",
        "advice": "自然に触れてみろ。深呼吸くらいはしとけ。"
    },
    {
        "color": "紫",
        "emotion": ["ちょっとカッコつけたい気分か？似合うといいけどな", "今日は神秘的なフリしとく？"],
        "trend": "感受性が高まり、インスピレーションが湧く日。",
        "advice": "アートとか音楽に触れてみ。意外とハマるかもな。"
    },
    {
        "color": "黒",
        "emotion": ["やっぱ黒だよな。無難で落ち着く", "今日は目立たず静かにしてろってことだ"],
        "trend": "自己防衛力・集中力が強まる。",
        "advice": "余計なこと言わずに黙って行動しろ。それが吉。"
    },
    {
        "color": "白",
        "emotion": ["白…だと？…純粋ぶってんじゃねぇよ", "まぁ…リセットって意味では悪くねぇか"],
        "trend": "初心に帰れる日。新しいことに向いてる。",
        "advice": "部屋を片付けろ。頭の中もスッキリすんぞ。"
    },
    {
        "color": "ピンク",
        "emotion": ["うわ…ピンクって…あんた本気？", "ま、優しくできるならやってみろよ"],
        "trend": "恋愛運や対人運がちょい高めの日。",
        "advice": "甘えたいなら素直に言え。たまにはな。"
    }
]

def run_lucky_color(user_id):
    lucky = random.choice(lucky_colors)
    return (
        f"🌈 ラッキーカラーは『{lucky['color']}』"
        f"クロネ：{random.choice(lucky['emotion'])}"
        f"🖍 色の傾向：{lucky['trend']}"
        f"🫖 アドバイス：{lucky['advice']}"
    )

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
    return f"【{card['name']}】意味：{card['meaning']}"

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
=======
# ==========================
# 🧩 Flask + LINE Webhook連携
# ==========================

from flask import Flask, request, abort
<<<<<<< HEAD
import os
import random

from linebot.v3.messaging import (
    MessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage,
    FlexMessage  # ←これ追加！
)

from linebot.v3.webhook import WebhookHandler
from linebot.v3.webhooks import MessageEvent
from linebot.exceptions import InvalidSignatureError
from linebot.v3.messaging import MessagingApiClient

app = Flask(__name__)
app = Flask(__name__)

# LINE APIの認証情報（セキュリティ的には環境変数推奨）
LINE_CHANNEL_ACCESS_TOKEN = 'tIyCE/XnhmCgdICOzqeU89R9MSi6j/AgbwaRGU+Dj4xlzDsw1sMJVC0MXL0X6dpOxid9jV2xU2OG1jVBpVCXTjEDKx44qH/yLLL8S4OWR6hsTYRqEusE/28rZSWntOuuROjtRo0H4N+XPj4mrIUoIQdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '4dc62a09bfc7d5f785dbba1538a0483b'

# v3対応LINE Bot初期化
line_bot_api = MessagingApiClient(LINE_CHANNEL_ACCESS_TOKEN)
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
=======
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


>>>>>>> 731eb27 (kurone_main.py追加)

# ==========================
# ① 会話ロジック（ユーザーとの対話・ステート管理）
# ==========================

user_states = {}
user_inputs = {}


<<<<<<< HEAD

@handler.add(MessageEvent)
=======
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

@handler.add(MessageEvent, message=TextMessage)
@handler.add(MessageEvent, message=TextMessage)
>>>>>>> 731eb27 (kurone_main.py追加)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text
    state = user_states.get(user_id, "start")
    reply = ""

    if "占い" in msg:
<<<<<<< HEAD
        flex_contents = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": "占い結果をここに表示"}
                ]
            }
        }
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[FlexMessage(alt_text="占い結果", contents=flex_contents)]
            )
        )
=======
        message = FlexSendMessage(alt_text="占い結果", contents={"type": "bubble", "body": {"type": "box", "layout": "vertical", "contents": [{"type": "text", "text": "占い結果をここに表示"}]}})
        line_bot_api.reply_message(event.reply_token, message)
>>>>>>> 731eb27 (kurone_main.py追加)
        return

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

    elif state == "choose_type":
        if msg in ["1", "相性", "相性診断"]:
            user_states[user_id] = "ask_name"
            reply = "クロネ：相性ぃ？ …知ってどうすんだよ。ま、いいけどな。まずはあんたの名前は？"
        elif msg in ["2", "タロット", "tarot"]:
            user_states[user_id] = "tarot"
<<<<<<< HEAD
            reply = "クロネ：タロットな…。オレの引きが冴えてるかどうか、試すってわけか。\n" + kurone_tarot_reading()
=======
            reply = "クロネ：タロットな…。オレの引きが冴えてるかどうか、試すってわけか。" + run_tarot_auto(user_id)
>>>>>>> 731eb27 (kurone_main.py追加)
        elif msg in ["3", "カラー", "ラッキーカラー", "色"]:
            user_states[user_id] = "lucky"
            reply = "クロネ：色ぉ？ …そういうの気にするタイプかよ。" + run_lucky_color(user_id)
        else:
            reply = "クロネ：そんな占いはねぇよ。ちゃんと【1〜3】の番号か、占いの名前を言えっての。"

    elif state == "ask_name":
        if user_id not in user_inputs:
            user_inputs[user_id] = {}
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
        except ValueError:
            reply = "クロネ：数字で月を言えっての。"

    elif state == "ask_birth_day":
        try:
            day = int(msg)
            if 1 <= day <= 31:
                user_inputs[user_id]["d1"] = day
                user_states[user_id] = "ask_partner_name"
                reply = "クロネ：気になってるヤツの名前は？"
            else:
                reply = "クロネ：1〜31の間で言え。常識な？"
        except ValueError:
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
        except ValueError:
            reply = "クロネ：数字で頼むわ。そいつの月な。"

    elif state == "ask_partner_day":
        try:
            day = int(msg)
            if 1 <= day <= 31:
                user_inputs[user_id]["d2"] = day
                user_states[user_id] = "done"
                name = user_inputs[user_id]["name"]
                partner = user_inputs[user_id]["partner"]
                m1 = user_inputs[user_id]["m1"]
                d1 = user_inputs[user_id]["d1"]
                m2 = user_inputs[user_id]["m2"]
                d2 = user_inputs[user_id]["d2"]
                result = run_compatibility(user_id, m1, d1, m2, d2)
                reply = (
                    f"クロネ：ふーん…じゃ、診てやるよ"
                    f"🧑‍💼 {name}🎯 {partner}"
                    f"{result}"
                    "……満足したか？また占いたいなら『占って』って言えよ。"
                )
            else:
                reply = "クロネ：日付ってのは1〜31の間だろ？常識。"
        except ValueError:
            reply = "クロネ：数字ってわかるか？日付だ、日付。"

    else:
        reply = "クロネ：……ったく、わかんねーなら最初から『占って』って言えよな。"

<<<<<<< HEAD
    line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply)]
        )
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
=======
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

if __name__ == "__main__":
    app.run()
>>>>>>> 731eb27 (kurone_main.py追加)


    # ※ 他のステート（ask_name以降）は別途追記する

<<<<<<< HEAD


=======
else:
        reply = (
            "クロネ：……ったく、わかんねーなら最初から『占って』って言えよな。"
        )

        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
@app.route("/")
def home():
    return "クロネ占いBotは動作中やで。LINEからメッセージ送ってや！"
>>>>>>> 731eb27 (kurone_main.py追加)


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


# ----- 🃏 タロットセリフ辞書（tarot_kurone_lines） -----
tarot_kurone_lines = {
    "愚者": {
        "過去": "なーんも考えんと突っ走ったツケ、今頃出とるだけやろ…",
        "現在": "はぁ…自由に見えて、ただの現実逃避ってこと、気づいてへんやろ",
        "未来": "落ちるとこまで落ちて、ようやく地に足つくかもな。でも、それも悪くない…かもな"
    },
    "魔術師": {
        "過去": "器用貧乏やったんちゃう？なんでも手出して、なんもモノになってへん",
        "現在": "始めるのはええけど、中身スカスカやったら意味ないで",
        "未来": "もし今の努力が実を結ぶなら…奇跡やな。でも、ないとは言わへんで"
    },
    "女教皇": {
        "過去": "分かったふりして距離置いてたやろ？ほんまは何も見えてなかったんちゃうか",
        "現在": "静かにしてたら正解が降ってくると思うてるん？甘いで",
        "未来": "本物の直感ってやつが出てくるかもな…それ、信じられたらの話やけど"
    },
    "女帝": {
        "過去": "甘やかされた結果が今のぬるい自分ちゃう？",
        "現在": "与えるとか包み込むとか…あんたにその余裕、あるんか？",
        "未来": "もし今、誰かをちゃんと大事にできるなら…それは誇ってええかもしれんな"
    },
    "皇帝": {
        "過去": "力でねじ伏せようとして、結局孤独になっただけやろ",
        "現在": "威厳とか言う前に、自分の不安隠すのやめたらどうや？",
        "未来": "もし誰かに背中見せられる日が来るなら…その時はちゃんと立て、絶対に"
    },
    "教皇": {
        "過去": "人の言うことばっか聞いて、自分の声無視してたんちゃう？",
        "現在": "教えとかルールって、時には毒になるねん。気づけや",
        "未来": "正しさに守られるんじゃなく、正しさを選べるなら…その時はちょっと、希望あるかもな"
    },
    "恋人": {
        "過去": "選ばれへんかったんは、お前のせいやろ",
        "現在": "自分の気持ちすらわからんのに、他人と向き合えるわけないやん",
        "未来": "もし本当に選ぶ覚悟ができたら…今度こそ、手放さずにすむかもな"
    },
    "戦車": {
        "過去": "突っ走ったはええけど、心はどっかに置いてきたんちゃう？",
        "現在": "勝ちたくて必死なんやろ？でも、何に勝つつもりやねん",
        "未来": "もし本気で進む覚悟があるなら…勝ち方も見えてくるかもな。オレも…ちょっと応援するわ"
    },
    "力": {
        "過去": "抑え込んでただけで、なんも克服できてへんやん",
        "現在": "強がってんの、バレバレやで",
        "未来": "ほんまの強さってのを見せてくれるんやったら…オレ、見届けてもええわ"
    },
    "隠者": {
        "過去": "逃げただけやん。ひとりになるのが楽やっただけやろ",
        "現在": "ほんまは誰かに気づいてほしいくせに、殻にこもってるとかダサいで",
        "未来": "その孤独が、いつか光に変わるなら…悪い未来やないな"
    },
    "運命の輪": {
        "過去": "チャンスやったかもしれへんけど、結局流されて終わりやったんちゃう",
        "現在": "運に頼るしかないって状況、もう詰んどるやん",
        "未来": "でもな、運命ってやつが味方してくれる瞬間も…たまにある。信じるかどうかはお前次第や"
    },
    "正義": {
        "過去": "バランス取ったつもりが、誰かに犠牲押し付けただけちゃう？",
        "現在": "自分が正しいって思いたいだけやろ。ほんまは揺らいでんのに",
        "未来": "もし本当に自分と向き合えるなら、ちょっとは救われるんかもな"
    },
    "吊るされた男": {
        "過去": "我慢したフリして、何も変える気なかっただけやろ",
        "現在": "動けへん言い訳して、自分から止まってんの気づいてる？",
        "未来": "それでも見方を変えたら…世界が少しマシに見えるかもな"
    },
    "死神": {
        "過去": "終わったのに、まだ引きずってるんアホらし",
        "現在": "変わるチャンス来とるのに、ビビって何もしてへんやん",
        "未来": "終わるからこそ始まるんや。…ま、終われたらの話やけどな"
    },
    "節制": {
        "過去": "どっちつかずで中途半端…そりゃ何も残らんわな",
        "現在": "うまくやろうとして、結局何にもできてへんやん",
        "未来": "ほんまの調和が訪れるなら…そろそろブレるのやめえや"
    },
    "悪魔": {
        "過去": "欲望に飲まれて、自分でも気づかんうちに腐っとったんちゃう？",
        "現在": "依存に気づかへんふりしてるけど、もう手遅れかもな",
        "未来": "でも、もしその鎖を自分で切れたら…ちょっとはマシな未来あるで"
    },
    "塔": {
        "過去": "全部崩れたんは、お前が見て見ぬふりしとったからやろ",
        "現在": "あーあ、今まさに崩れてるとこやん。どうすんのこれ？",
        "未来": "ゼロからでも、建て直せる力があるなら…まだ終わりやないな"
    },
    "星": {
        "過去": "希望持ったフリして、何にもしてへんかったんちゃう？",
        "現在": "理想語るのはええけど、現実見えてへんやろ",
        "未来": "…それでも、その光を信じたいって思えるなら、ええ夢かもな"
    },
    "月": {
        "過去": "不安に流されて、現実も夢もぐちゃぐちゃやったやろ",
        "現在": "目の前のこと、ほんまに見えてるんか？全部幻ちゃうんか",
        "未来": "それでも迷いながら進めるなら…ちょっとは価値あるかもしれんな"
    },
    "太陽": {
        "過去": "楽しそうに見えて、結局見栄やっただけちゃう？",
        "現在": "幸せそうやけど…それ、ホンマに本心か？演じてへん？",
        "未来": "…でもな、今度こそ心から笑えるなら、それは…羨ましいかもな"
    },
    "審判": {
        "過去": "後悔ばっかで、何ひとつ清算できてへんやん",
        "現在": "過去に引きずられて、今を捨てるとかアホすぎやろ",
        "未来": "ほんまに向き合えたら、生まれ変われるかもしれへんな…一応、な"
    },
    "世界": {
        "過去": "完璧求めすぎて、自分でも疲れとったんちゃう？",
        "現在": "今が完成形とか思ってへんよな？ただの終わりに見えるで",
        "未来": "それでも、ほんまに全うできたなら…オレ、ちょっとだけ認めたるわ"
    }
}

# ----- 🃏 タロット占い（3枚引き） -----

tarot_scores = {
    # 🌟 超吉（+3）
    "太陽": 3,
    "世界": 3,
    "星": 3,

    # 👍 吉（+2）
    "恋人": 2,
    "戦車": 2,
    "審判": 2,

    # 🙂 小吉（+1）
    "力": 1,
    "皇帝": 1,
    "節制": 1,

    # 😐 平（0）
    "魔術師": 0,
    "正義": 0,
    "教皇": 0,
    "愚者": 0,

    # 🙁 小凶（-1）
    "女教皇": -1,
    "隠者": -1,
    "月": -1,
    "吊るされた男": -1,

    # 😖 凶（-2）
    "死神": -2,
    "悪魔": -2,

    # 💀 大凶（-3）
    "塔": -3
}

# ----- 🃏 タロット占い（3枚引き） -----
def kurone_tarot_reading():

    
    cards = list(tarot_kurone_lines.keys())
    selected = random.sample(cards, 3)
    positions = ["過去", "現在", "未来"]

    intro = "🐾 カサカサ…クロネが無言でカードを3枚並べた。\n"
    intro += "💭「ったく、こんなもん占ってどうすんだよ……」\n"
    intro += "でも…少しだけ本気になったようだ。\n"

    result = "🔮 【タロット3枚引き】\n" + intro

    total_score = 0

    for i in range(3):
        card = selected[i]
        pos = positions[i]
        line = tarot_kurone_lines[card][pos]
        score = tarot_scores.get(card, 0)
        total_score += score
        result += f"\n━━━\n【{pos}】🃏{card}（{score:+d}）\n💭クロネ「{line}」\n"

    # 💯 スコア評価コメント
    if total_score >= 6:
        comment = "…オレが言うのもアレやけど、運命の寵児ちゃうか？"
    elif total_score >= 3:
        comment = "お前にしては…まぁ上出来やな"
    elif total_score >= 1:
        comment = "まぁ…悪くはないんちゃう？"
    elif total_score >= -1:
        comment = "うーん、微妙やな"
    elif total_score >= -4:
        comment = "正直、調子悪そやな"
    else:
        comment = "……今日は寝とけ"

    result += f"\n━━━\n💯 総合スコア：{total_score:+d}（{comment}）"

    return result


def create_tarot_flex():
    cards = list(tarot_kurone_lines.keys())
    selected = random.sample(cards, 3)
    positions = ["過去", "現在", "未来"]
    bubbles = []

    for i in range(3):
        card = selected[i]
        pos = positions[i]
        line = tarot_kurone_lines[card][pos]
        score = tarot_scores.get(card, 0)

        bubble = {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {"type": "text", "text": f"【{pos}】🃏{card}", "weight": "bold", "size": "lg"},
                    {"type": "text", "text": f"スコア：{score:+d}", "size": "sm", "color": "#999999"},
                    {"type": "box", "layout": "horizontal", "contents": [
                        {"type": "text", "text": f"💭 クロネ「{line}」", "wrap": True, "size": "sm"}
                    ]}
                ]
            }
        }
        bubbles.append(bubble)

    # 複数バブルをcarousel形式で返す
    flex = {
        "type": "carousel",
        "contents": bubbles
    }

<<<<<<< HEAD
    return FlexMessage(alt_text="クロネのタロット占い結果", contents=flex)
=======
    return FlexSendMessage(alt_text="クロネのタロット占い結果", contents=flex)
>>>>>>> 731eb27 (kurone_main.py追加)

# ----- 🌈 ラッキーカラー占い -----
lucky_colors = [
    {
        "color": "赤",
        "emotion": ["今日は燃えてるな…気合だけは認めてやる", "アツくなりすぎて空回りすんなよ"],
        "trend": "行動力と情熱が高まりやすい日。",
        "advice": "言いたいことはちゃんと口に出せ。ただしケンカ腰はやめとけ。"
    },
    {
        "color": "青",
        "emotion": ["冷静？オレには無理だな。あんたは頑張れ", "心、落ち着かせとけ。うるさいの苦手だから"],
        "trend": "判断力が増して集中しやすい。",
        "advice": "静かな場所で考え事するといいかもな。人の話はよく聞けよ。"
    },
    {
        "color": "黄",
        "emotion": ["元気に見せとけば何とかなる…かもな", "明るく振る舞うのって、けっこう疲れるんだぞ？"],
        "trend": "好奇心と社交性が高まる日。",
        "advice": "人と話すのも悪くない。ただし無理すんなよ。"
    },
    {
        "color": "緑",
        "emotion": ["穏やか？…らしくねぇけど今日はそれでいい", "のんびりしすぎて腐るなよ"],
        "trend": "バランス感覚と癒しがテーマ。",
        "advice": "自然に触れてみろ。深呼吸くらいはしとけ。"
    },
    {
        "color": "紫",
        "emotion": ["ちょっとカッコつけたい気分か？似合うといいけどな", "今日は神秘的なフリしとく？"],
        "trend": "感受性が高まり、インスピレーションが湧く日。",
        "advice": "アートとか音楽に触れてみ。意外とハマるかもな。"
    },
    {
        "color": "黒",
        "emotion": ["やっぱ黒だよな。無難で落ち着く", "今日は目立たず静かにしてろってことだ"],
        "trend": "自己防衛力・集中力が強まる。",
        "advice": "余計なこと言わずに黙って行動しろ。それが吉。"
    },
    {
        "color": "白",
        "emotion": ["白…だと？…純粋ぶってんじゃねぇよ", "まぁ…リセットって意味では悪くねぇか"],
        "trend": "初心に帰れる日。新しいことに向いてる。",
        "advice": "部屋を片付けろ。頭の中もスッキリすんぞ。"
    },
    {
        "color": "ピンク",
        "emotion": ["うわ…ピンクって…あんた本気？", "ま、優しくできるならやってみろよ"],
        "trend": "恋愛運や対人運がちょい高めの日。",
        "advice": "甘えたいなら素直に言え。たまにはな。"
    }
]

def run_lucky_color(user_id):
    lucky = random.choice(lucky_colors)
    return (
        f"🌈 ラッキーカラーは『{lucky['color']}』"
        f"クロネ：{random.choice(lucky['emotion'])}"
        f"🖍 色の傾向：{lucky['trend']}"
        f"🫖 アドバイス：{lucky['advice']}"
    )

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
    return f"【{card['name']}】意味：{card['meaning']}"

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
<<<<<<< HEAD
=======


>>>>>>> 731eb27 (kurone_main.py追加)
>>>>>>> b75c51b5d766a51656ee49af0e99299735eef038
