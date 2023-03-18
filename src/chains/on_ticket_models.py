import re
from typing import ClassVar, Literal, Self, Type

import openai
from loguru import logger

from pydantic import BaseModel


ChatModel = Literal["gpt-3.5-turbo"] | Literal["gpt-4"]


class Message(BaseModel):
    role: Literal["system"] | Literal["user"] | Literal["assistant"]
    content: str


class ChatGPT(BaseModel):
    messages: list[Message] = [
        Message(
            role="system", content="You are a helpful assistant software developer."
        )
    ]
    prev_message_states: list[list[Message]] = []
    model: ChatModel = "gpt-4"

    def chat(self, content: str, model: ChatModel | None = None):
        if model is None:
            model = self.model
        self.prev_message_states.append(self.messages)
        self.messages.append(Message(role="user", content=content))
        # response = call_chatgpt(self.messages_dicts, model=model)
        response = self.call_openai(model=model)
        self.messages.append(Message(role="assistant", content=response))
        return self.messages[-1].content

    def call_openai(self, model: ChatModel):
        # TODO: use Tiktoken
        messages_length = (
            sum([message.content.count(" ") for message in self.messages]) * 1.5
        )
        max_tokens = 8192 - int(messages_length) - 1000
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

    @property
    def messages_dicts(self):
        return [message.dict() for message in self.messages]

    def undo(self):
        if len(self.prev_message_states) > 0:
            self.messages = self.prev_message_states.pop()
        return self.messages


# Self = TypeVar("Self", bound="RegexMatchableBaseModel")

class RegexMatchableBaseModel(BaseModel):
    _regex: ClassVar[str]

    @classmethod
    def from_string(cls: Type[Self], string: str) -> Self:
        # match = re.search(file_regex, string, re.DOTALL)
        match = re.search(cls._regex, string, re.DOTALL)
        if match is None:
            raise ValueError("Did not match")
        return cls(**{k: v.strip() for k, v in match.groupdict().items()})


class FileChange(RegexMatchableBaseModel):
    filename: str
    description: str
    code: str
    _regex = r"""(?P<filename>.*)Description:(?P<description>.*)```([a-zA-Z0-9]+\n)?(?P<code>.*)```"""  # noqa: E501


class PullRequest(RegexMatchableBaseModel):
    title: str
    content: str
    _regex = r"""Title:(?P<title>.*)Content:(?P<content>.*)"""
