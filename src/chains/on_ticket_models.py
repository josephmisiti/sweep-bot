from src.utils.tiktoken_utils import count_tokens

class ChatGPT(BaseModel):
    ...
    def call_openai(self, model: ChatModel):
        messages_length = sum([count_tokens(message.content) for message in self.messages])
        max_tokens = 8192 - messages_length - 1000
        result = (
            openai.ChatCompletion.create(
                model=model,
                messages=self.messages_dicts,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            .choices[0]
            .message["content"]
        )
        logger.info(f"Input:\n{self.messages}\n\nOutput:\n{result}")
        return result
    ...