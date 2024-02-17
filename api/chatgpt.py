from api.prompt import Prompt
import os
from openai import OpenAI
client = OpenAI()

client.api_key = os.getenv("OPENAI_API_KEY")


class ChatGPT:
    def __init__(self):
        self.prompt = Prompt()
        self.model = os.getenv("OPENAI_MODEL", default = "gpt-4-turbo-preview")
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", default = 0.2))
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", default = 2000))

    def get_response(self):
        # 使用stream=True來初始化資料流
        stream = client.chat.completions.create(
            model=self.model,
            messages=self.prompt.generate_prompt(),
            stream=True,
        )
        responses = []
        for chunk in stream:
            # 檢查是否有新的內容被發送
            if chunk.choices[0].delta.content is not None:
                responses.append(chunk.choices[0].delta.content)
        # 將收集到的所有片段組合成一個完整的回應
        return ''.join(responses)

    def add_msg(self, text):
        self.prompt.add_msg(text)
