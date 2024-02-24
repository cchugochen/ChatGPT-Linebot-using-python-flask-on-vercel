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
    return 'Hello, World! This is a linebot with GPT and Flask'

@app.route("/webhook", methods=['POST']) # 定義Webhook路徑的處理函數，用於接收並處理LINE平台的事件通知
def callback():
    signature = request.headers['X-Line-Signature']
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
    msg = event.message.text.strip()
    
    user_id = event.source.user_id  # 取得 userID
    file_path = f'log/{user_id}.txt'  # 定義用戶對話記錄的文件路徑
    if not os.path.exists('log'):
        os.makedirs('log')

    # 對話記錄管理
    if msg.startswith('remove'):
        open(file_path, 'w').write("")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Your record has been cleared!'))
        return
    else:
        with open(file_path, 'a+', encoding='utf-8') as file:
            file.write(msg + '\n')
            file.seek(0)
            conversation = file.read()
            
        # 確保只保留最近 2000 字元
        if len(conversation) > 2000:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(conversation[-2000:])

    activation_sign = "@#" # 定義機器人被啟用的訊息開頭標記
    
    if not event.message.text.startswith(activation_sign):
        # 如果消息不是以特定標記開頭，則不處理這條消息
        return
    actual_message = event.message.text[len(activation_sign):].strip()

    if event.message.type != "text":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我只能看得懂文字"))
        return

    if event.message.text == "Oo**":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我可以說話囉，歡迎來跟我互動"))
        return

    if event.message.text == "Xx**":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴"))
        return
    
    if working_status:
        chatgpt.add_msg(f"user: {actual_message}\n")
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
