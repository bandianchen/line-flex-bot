from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)
import json

app = Flask(__name__)

# 填入你自己的 token / secret
import os
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

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
      {
        "type": "text",
        "text": "開始填寫需求評估",
        "weight": "bold",
        "size": "xl",
        "color": "#333333"
      },
      {
        "type": "text",
        "text": "只需 10 秒，回答三個問題，協助媒合最適合的設計師！",
        "wrap": True,
        "margin": "md",
        "color": "#666666",
        "size": "sm"
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "spacing": "md",
    "contents": [
      {
        "type": "button",
        "style": "primary",
        "action": {
          "type": "message",
          "label": "開始填寫",
          "text": "Q1 屋齡"
        },
        "color": "#00A2E8"
      }
    ]
  }
}

# -------------------------
# Flex：問題 1（屋齡）
# -------------------------
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
        "margin": "md",
        "contents": [
          {"type": "button", "action": {"type": "message", "label": "0-5 年", "text": "屋齡 0-5"}},
          {"type": "button", "action": {"type": "message", "label": "5-10 年", "text": "屋齡 5-10"}},
          {"type": "button", "action": {"type": "message", "label": "10-20 年", "text": "屋齡 10-20"}},
          {"type": "button", "action": {"type": "message", "label": "20-30 年", "text": "屋齡 20-30"}},
          {"type": "button", "action": {"type": "message", "label": "30 年以上", "text": "屋齡 30+"}}
        ]
      }
    ]
  }
}

# -------------------------
# Flex：問題 2（坪數）
# -------------------------
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

# -------------------------
# Flex：問題 3（預算）
# -------------------------
flex_q3 = {
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {"type": "text", "text": "問題 3：預算（室內設計）", "weight": "bold", "size": "xl"},
      {"type": "text", "text": "請選擇您的預算範圍：", "margin": "md"},
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {"type": "button", "action": {"type": "message", "label": "50–100 萬", "text": "預算 50-100"}},
          {"type": "button", "action": {"type": "message", "label": "100–150 萬", "text": "預算 100-150"}},
          {"type": "button", "action": {"type": "message", "label": "150–250 萬", "text": "預算 150-250"}},
          {"type": "button", "action": {"type": "message", "label": "250 萬以上", "text": "預算 250+"}}
        ]
      }
    ]
  }
}

# -------------------------
# Webhook 接收訊息
# -------------------------
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# -------------------------
# 文字事件處理
# -------------------------
@handler.add(MessageEvent, MessageEvent.message_type == 'text')
def handle_message(event):
    text = event.message.text

    # Step 1：觸發流程
    if text == "開始填寫需求評估":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="開始填寫", contents=flex_start)
        )
        return

    # Step 2：問題 1
    if text == "Q1 屋齡":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="屋齡", contents=flex_q1)
        )
        return

    # Step 3：問題 2
    if text.startswith("屋齡"):
        # 在這裡你可以加入 API 貼標籤
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="坪數", contents=flex_q2)
        )
        return

    # Step 4：問題 3
    if text.startswith("坪數"):
        # 在這裡你可以加入 API 貼標籤
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="預算", contents=flex_q3)
        )
        return

    # Step 5：流程結束
    if text.startswith("預算"):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage("感謝您的填寫！我們稍後會有專人與您聯繫 😊")
        )
        return


if __name__ == "__main__":
    app.run(port=8000)
