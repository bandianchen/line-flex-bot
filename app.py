import os
from flask import Flask, request, abort, send_from_directory, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)

app = Flask(__name__)

# -------------------------
# 讀取 Render 環境變數
# -------------------------
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 你的 Render 公網網址（請務必填）
# 例：https://line-flex-bot.onrender.com
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://YOUR_RENDER_DOMAIN.onrender.com")

if not LINE_CHANNEL_ACCESS_TOKEN:
    raise ValueError("Missing LINE_CHANNEL_ACCESS_TOKEN environment variable.")
if not LINE_CHANNEL_SECRET:
    raise ValueError("Missing LINE_CHANNEL_SECRET environment variable.")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


# =========================================================
# LIFF 頁面與接收 API
# =========================================================

# 提供 LIFF 表單頁（liff.html 必須在 repo 根目錄）
@app.route("/liff", methods=["GET"])
def liff_page():
    return send_from_directory(".", "liff.html")


# 接收 LIFF 表單送出的電話
@app.route("/api/lead", methods=["POST"])
def api_lead():
    data = request.get_json(force=True)

    user_id = data.get("userId")
    phone = data.get("phone")
    name = data.get("displayName", "")

    if not user_id or not phone:
        return jsonify({"ok": False, "error": "missing userId/phone"}), 400

    # TODO: 之後你要寫入 Supabase / Google Sheet
    print("NEW LEAD:", {"userId": user_id, "name": name, "phone": phone})

    # 可選：主動推播確認訊息給用戶
    try:
        line_bot_api.push_message(
            user_id,
            TextSendMessage(f"{name}，已收到您的電話 {phone}，設計顧問將盡快與您聯繫 😊")
        )
    except Exception as e:
        print("push failed:", e)

    return jsonify({"ok": True})


# =========================================================
# Flex Messages
# =========================================================

# Flex：開始填寫需求評估
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
          {"type": "button", "action": {"type": "message", "label": "50–100 萬", "text": "預算 50-100"}},
          {"type": "button", "action": {"type": "message", "label": "100–150 萬", "text": "預算 100-150"}},
          {"type": "button", "action": {"type": "message", "label": "150–250 萬", "text": "預算 150-250"}},
          {"type": "button", "action": {"type": "message", "label": "250 萬以上", "text": "預算 250+"}}
        ]
      }
    ]
  }
}


def make_liff_flex():
    """預算答完後導 LIFF 的 Flex"""
    liff_url = f"{PUBLIC_BASE_URL}/liff"
    return {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {"type": "text", "text": "最後一步：留下聯絡電話", "weight": "bold", "size": "xl"},
          {
            "type": "text",
            "text": "按下按鈕開啟表單，手機會自動顯示電話建議，你只要點一下就完成 😊",
            "wrap": True,
            "margin": "md",
            "size": "sm"
          }
        ]
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "button",
            "style": "primary",
            "action": {"type": "uri", "label": "開啟電話表單", "uri": liff_url}
          }
        ]
      }
    }


# =========================================================
# Webhook（唯一一份 /callback）
# =========================================================
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# =========================================================
# 事件處理
# =========================================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()

    # Step 0：手動輸入觸發開始
    if text == "開始填寫需求評估":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="開始填寫", contents=flex_start)
        )
        return

    # Step 1：進 Q1
    if text == "Q1 屋齡":
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="屋齡", contents=flex_q1)
        )
        return

    # Step 2：答屋齡 → 進 Q2
    if text.startswith("屋齡"):
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="坪數", contents=flex_q2)
        )
        return

    # Step 3：答坪數 → 進 Q3
    if text.startswith("坪數"):
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="預算", contents=flex_q3)
        )
        return

    # Step 4：答預算 → 導 LIFF
    if text.startswith("預算"):
        flex_to_liff = make_liff_flex()
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text="留下電話", contents=flex_to_liff)
        )
        return


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
