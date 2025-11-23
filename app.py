import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

app = Flask(__name__)

# 環境變數讀取（Render 會從 Environment 填入）
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 防呆：如果沒設定環境變數 → 直接報錯
if not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("Missing LINE_CHANNEL_ACCESS_TOKEN environment variable.")
if not LINE_CHANNEL_SECRET:
    raise ValueError("Missing LINE_CHANNEL_SECRET environment variable.")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# -------------------------
# Flex：開始填寫需求評估
# -------------------------
flex_start = {
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover"
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {"type": "text", "text": "開始填寫需求評估", "weight": "bold", "size": "xl"},
      {"type": "text", "text": "回答三個問題，我們幫你媒合最適合的設計師！", "wrap": True, "margin": "md"}
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "button",
        "style": "primary",
        "action": {"type": "message", "label": "開始填寫", "text": "Q1 屋齡"}
      }
    ]
  }
}

# Flex：問題 1（屋齡）
flex_q1 = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {"type": "text", "text": "問題 1：屋齡", "weight": "bold", "size": "xl"},
      {"type": "text", "text": "請選擇以下其中一項：", "margin": "md"},
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {"type": "button", "action": {"type": "message", "label": "0–5 年", "text": "屋齡 0-5"}},
          {"type": "button", "action": {"type": "message", "label": "5–10 年", "text": "屋齡 5-10"}},
          {"type": "button", "action": {"type": "message", "label": "10–20 年", "text": "屋齡 10-20"}},
          {"type": "button", "action": {"type": "message", "label": "20–30 年", "text": "屋齡 20-30"}},
          {"type": "button", "action": {"type": "message", "label": "30 年以上", "text": "屋齡 30+"}}
        ]
      }
    ]
  }
}

# Flex：問題 2（坪數）
flex_q2 = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {"type": "text", "text": "問題 2：坪數", "weight": "bold", "size": "xl"},
      {"type": "text", "text": "請選擇以下其中一項：", "margin": "md"},
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {"type": "button", "action": {"type": "message", "label": "10 坪以下", "text": "坪數 <=10"}},
          {"type": "button", "action": {"type": "message", "label": "10–20 坪", "text": "坪數 10-20"}},
          {"type": "button", "action": {"type": "message", "label": "20–30 坪", "text": "坪數 20-30"}},
          {"type": "button", "action": {"type": "message", "label": "30 坪以上", "text": "坪數 30+"}}
        ]
      }
    ]
  }
}

# Flex：問題 3（預算）
flex_q3 = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {"type": "text", "text": "問題 3：預算（室內設計）", "weight": "bold", "size": "xl"},
      {"type": "text", "text": "請選擇您的預算：", "margin": "md"},
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {"type": "button", "action": {"type": "message", "label": "150–200 萬", "text": "預算 150-200"}},
          {"type": "button", "action": {"type": "message", "label": "200–250 萬", "text": "預算 200-250"}},
          {"type": "button", "action": {"type": "message", "label": "250–300 萬", "text": "預算 250-300"}},
          {"type": "button", "action": {"type": "message", "label": "300 萬以上", "text": "預算 300+"}}
        ]
      }
    ]
  }
}


# -------------------------
# Webhook 路由（唯一版本，不能重複）
# -------------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# -------------------------
# 處理文字訊息事件
# -------------------------
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text

    # Step 1：開始流程
    if text == "開始填寫需求評估":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="開始填寫", contents=flex_start)
        )
        return

    # Step 2：進入 Q1
    if text == "Q1 屋齡":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="屋齡", contents=flex_q1)
        )
        return

    # Step 3：回答 Q1 → 進 Q2
    if text.startswith("屋齡"):
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="坪數", contents=flex_q2)
        )
        return

    # Step 4：回答 Q2 → 進 Q3
    if text.startswith("坪數"):
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="預算", contents=flex_q3)
        )
        return

    # Step 5：回答 Q3 → 完成
    if text.startswith("預算"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("感謝您的填寫！設計顧問將盡快與您聯繫 😊")
        )
        return


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
