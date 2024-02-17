import os

chat_language = os.getenv("INIT_LANGUAGE", default = "zh-TW")

# 從環境變數設定訊息列表上限，若未設定則預設為7
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 7))
LANGUAGE_TABLE = {
  "zh-TW": "哈囉！",
  "en": "Hello!"
}

AI_GUIDELINES = 'You are a helpful assistant. Using zh-TW mainly, but maintain English(or original text) for professional terms.'

class Prompt: # 定義Prompt類別，用於管理對話訊息
    def __init__(self): # 初始化訊息列表並添加系統訊息，包含問候語和AI指南
        self.msg_list = [] 
        self.msg_list.append(
            {
                "role": "system", 
                "content": f"{LANGUAGE_TABLE[chat_language]} + {AI_GUIDELINES})"
             })    
    def add_msg(self, new_msg):  # 添加新訊息到訊息列表中，如果列表已滿則移除最舊的訊息
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.msg_list.pop(0)
        self.msg_list.append({"role": "user", "content": new_msg})

    def generate_prompt(self):
        return self.msg_list