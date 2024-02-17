from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from api.chatgpt import ChatGPT

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFAULT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# domain root
@app.route('/') # 定義根路徑的處理函數，當訪問根路徑時返回歡迎信息
def home():
    return 'Hello, World! This is a linebot with GPT-3.5 and Flask'

@app.route("/webhook", methods=['POST']) # 定義Webhook路徑的處理函數，用於接收並處理LINE平台的事件通知
def callback():
    # 獲取請求頭中的X-Line-Signature值，用於後續的驗證
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try: # 嘗試處理Webhook通知內容
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status # 引用全局變量以改變機器人的對話狀態
    if event.message.type != "text":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我只能處理文字"))
        return

    if event.message.text == "Oo**":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我可以說話囉，歡迎來跟我互動 ^_^ "))
        return

    if event.message.text == "Xx**":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴 > < "))
        return
    
    if working_status:
        chatgpt.add_msg(f"user: {event.message.text}\n")
        # 將原本的chatgpt.get_response()調用包裹在try-except塊中
        try:
            reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        except Exception as e:
            app.logger.error(f"Error while getting response from ChatGPT: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="很抱歉，我現在無法回答您的問題，請稍後再試。")
            )
            return  # 發生異常時終止函數執行
        
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))

if __name__ == "__main__":
    app.run()
