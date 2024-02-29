from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI

import os

# 環境變數配置
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFAULT_TALKING", default = "true").lower() == "true"
user_conversations = {} # 使用字典來暫時儲存用戶的對話記錄

app = Flask(__name__)

AI_SYS_PROMPT = 'I am are a helpful assistant. Using zh-TW mainly, but maintain English(or original text) for professional terms.'

class ChatGPT:
    def __init__(self):
        self.messages = []

    def add_msg(self, user_id, text):
        full_text = f"{user_conversations.get(user_id, AI_SYS_PROMPT)}\n{text}"
        # Ensure the conversation does not exceed 2000 characters, keep the latest 2000 characters
        user_conversations[user_id] = full_text[-2000:]

    def get_response(self, user_id):
        messages = [{"role": "system", "content": AI_SYS_PROMPT}] if user_id not in user_conversations else []
        messages += [{"role": "user", "content": msg} for msg in user_conversations[user_id].split('\n')]

        response = client.chat.completions.create(
            model='gpt-3.5-turbo-0125',
            messages=messages,
            temperature=0.2,
            max_tokens=1500,
        )
        return response.choices[0].message.content

chatgpt = ChatGPT()  #模組chatgpt函數

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

    user_id = event.source.user_id  # 取得 userID
    msg = event.message.text.strip()

    if not msg.startswith("@#"):
        return  # 如果消息不是以特定標記開頭，則不處理這條消息
    
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
        actual_message = actual_message = msg[len("@#"):].strip()
        
         # Prepend user's previous conversation to the actual_message
        chatgpt.add_msg(user_id, actual_message)
        # 將原本的chatgpt.get_response()調用包裹在try-except塊中
        try:
            reply_msg = chatgpt.get_response(user_id)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_msg))
        except Exception as e:
            app.logger.error(f"Error while getting response from ChatGPT: {e}")
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="很抱歉，我現在無法回答您的問題，請稍後再試。")
            )
            return  # 發生異常時終止函數執行

if __name__ == "__main__":
    app.run()
