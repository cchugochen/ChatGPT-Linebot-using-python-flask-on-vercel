import os
from openai import OpenAI

# 環境變數配置
client = OpenAI()
client.api_key = os.getenv("OPENAI_API_KEY")
chat_language = os.getenv("INIT_LANGUAGE", default="zh-TW")
MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default=20))
LANGUAGE_TABLE = {
    "zh-TW": "哈囉！",
    "en": "Hello!"
}
AI_GUIDELINES = 'I am are a helpful assistant. Using zh-TW mainly, but maintain English(or original text) for professional terms.'

class Prompt:
    def __init__(self):
        self.msg_list = [] 
        self.msg_list.append({
            "role": "system", 
            "content": f"{LANGUAGE_TABLE[chat_language]} + {AI_GUIDELINES})"
        })

    def add_msg(self, new_msg):
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.msg_list.pop(0)
        self.msg_list.append({"role": "user", "content": new_msg})

    def generate_prompt(self):
        return self.msg_list

class ChatGPT:
    def __init__(self):
        self.prompt = Prompt()
        self.model = os.getenv("OPENAI_MODEL", default="gpt-4-Turbo-preview")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default=0.2))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default=3000))

    def get_response(self):
        stream = client.chat.completions.create(
            model=self.model,
            messages=self.prompt.generate_prompt(),
            stream=True,
        )
        responses = []
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                responses.append(chunk.choices[0].delta.content)
        return ''.join(responses)

    def add_msg(self, text):
        self.prompt.add_msg(text)