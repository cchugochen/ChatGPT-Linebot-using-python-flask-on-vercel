import os

chat_language = os.getenv("INIT_LANGUAGE", default = "zh-TW")

MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default = 7))
LANGUAGE_TABLE = {
  "zh-TW": "哈囉！這是雨果的GPT-4筆記小助理",
  "en": "Hello!"
}

AI_GUIDELINES = 'You are a bright teacher and good at communication in Taiwan culture. 一開始用繁體中文回答. If the input content academic-like request, Provide user a point wise academic summary with proper title. 專有名詞使用原文或英文.'

class Prompt:
    def __init__(self):
        self.msg_list = []
        self.msg_list.append(
            {
                "role": "system", 
                "content": f"{LANGUAGE_TABLE[chat_language]}, {AI_GUIDELINES})"
             })    
    def add_msg(self, new_msg):
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.msg_list.pop(0)
        self.msg_list.append({"role": "user", "content": new_msg})

    def generate_prompt(self):
        return self.msg_list