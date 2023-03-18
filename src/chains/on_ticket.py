"""
On Github ticket, get ChatGPT to deal with it
"""

import re
from typing import Literal
from pydantic import BaseModel
import os
import openai
import subprocess
from github import Github, GithubException, ContentFile

from src.chains.on_ticket_prompts import human_message_prompt, pr_code_prompt, pr_text_prompt

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)

file_regex = r'''(?P<filename>.*)Description:(?P<description>.*)\n*```([a-zA-Z0-9]+\n)?(?P<code>.*)```'''
pr_code_regex = r'''```(?P<code>.*)```'''
pr_texts_regex = r'''Title:(?P<title>.*)Content:(?P<content>.*)'''

def make_valid_string(string: str):
    pattern = r'[^\w./-]+'
    return re.sub(pattern, ' ', string)

ChatModel = Literal["gpt-3.5-turbo"] | Literal["gpt-4"]

def call_chatgpt(messages: dict, model: ChatModel ="gpt-4"):
    messages_length = sum([message["content"].count(" ") for message in messages]) * 1.5
    max_tokens = 8192 - int(messages_length)
    return openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.
    ).choices[0].message["content"]

class Message(BaseModel):
    role: Literal["system"] | Literal["user"] | Literal["assistant"]
    content: str

class ChatGPT(BaseModel):
    messages: list[Message] = [Message(role="system", content="You are a helpful assistant software developer.")]
    prev_message_states: list[list[Message]] = []
    model: ChatModel = "gpt-4"

    def chat(self, content: str, model: ChatModel | None = None):
        if model is None:
            model = self.model
        self.prev_message_states.append(self.messages)
        self.messages.append(Message(role="user", content=content))
        response = call_chatgpt(self.messages_dicts, model=model)
        self.messages.append(Message(role="assistant", content=response))
        return self.messages[-1].content
    
    @property
    def messages_dicts(self):
        return [message.dict() for message in self.messages]
    
    def undo(self):
        if len(self.prev_message_states) > 0:
            self.messages = self.prev_message_states.pop()
        return self.messages
    

default_relevant_directories = """
langchain/memory
    buffer.py
    chat_memory.py
    entity.py
    kg.py
    readonly.py
    summary_buffer.py
    utils.py
    buffer_window.py
    combined.py
    __init__.py
    prompt.py
    simple.py
    summary.py
"""

default_relevant_files = '''
"""
File: langchain/memory/__init__.py
"""


from langchain.memory.buffer import (
    ConversationBufferMemory,
    ConversationStringBufferMemory,
)
from langchain.memory.buffer_window import ConversationBufferWindowMemory
from langchain.memory.chat_memory import ChatMessageHistory
from langchain.memory.combined import CombinedMemory
from langchain.memory.entity import ConversationEntityMemory
from langchain.memory.kg import ConversationKGMemory
from langchain.memory.readonly import ReadOnlySharedMemory
from langchain.memory.simple import SimpleMemory
from langchain.memory.summary import ConversationSummaryMemory
from langchain.memory.summary_buffer import ConversationSummaryBufferMemory

__all__ = [
    "CombinedMemory",
    "ConversationBufferWindowMemory",
    "ConversationBufferMemory",
    "SimpleMemory",
    "ConversationSummaryBufferMemory",
    "ConversationKGMemory",
    "ConversationEntityMemory",
    "ConversationSummaryMemory",
    "ChatMessageHistory",
    "ConversationStringBufferMemory",
    "ReadOnlySharedMemory",
]


"""
File: langchain/memory/summary_buffer.py
"""


from typing import Any, Dict, List

from pydantic import BaseModel, root_validator

from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.summary import SummarizerMixin
from langchain.memory.utils import get_buffer_string
from langchain.schema import BaseMessage, SystemMessage


class ConversationSummaryBufferMemory(BaseChatMemory, SummarizerMixin, BaseModel):
    """Buffer with summarizer for storing conversation memory."""

    max_token_limit: int = 2000
    moving_summary_buffer: str = ""
    memory_key: str = "history"

    @property
    def buffer(self) -> List[BaseMessage]:
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.
        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Return history buffer."""
        buffer = self.buffer
        if self.moving_summary_buffer != "":
            first_messages: List[BaseMessage] = [
                SystemMessage(content=self.moving_summary_buffer)
            ]
            buffer = first_messages + buffer
        if self.return_messages:
            final_buffer: Any = buffer
        else:
            final_buffer = get_buffer_string(
                buffer, human_prefix=self.human_prefix, ai_prefix=self.ai_prefix
            )
        return {self.memory_key: final_buffer}

    @root_validator()
    def validate_prompt_input_variables(cls, values: Dict) -> Dict:
        """Validate that prompt input variables are consistent."""
        prompt_variables = values["prompt"].input_variables
        expected_keys = {"summary", "new_lines"}
        if expected_keys != set(prompt_variables):
            raise ValueError(
                "Got unexpected prompt input variables. The prompt expects "
                f"{prompt_variables}, but it should have {expected_keys}."
            )
        return values

    def get_num_tokens_list(self, arr: List[BaseMessage]) -> List[int]:
        """Get list of number of tokens in each string in the input array."""
        return [self.llm.get_num_tokens(get_buffer_string([x])) for x in arr]

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        super().save_context(inputs, outputs)
        # Prune buffer if it exceeds max token limit
        buffer = self.chat_memory.messages
        curr_buffer_length = sum(self.get_num_tokens_list(buffer))
        if curr_buffer_length > self.max_token_limit:
            pruned_memory = []
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = sum(self.get_num_tokens_list(buffer))
            self.moving_summary_buffer = self.predict_new_summary(
                pruned_memory, self.moving_summary_buffer
            )

    def clear(self) -> None:
        """Clear memory contents."""
        super().clear()
        self.moving_summary_buffer = ""


"""
File: langchain/memory/chat_memory.py 
"""


from abc import ABC
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from langchain.memory.utils import get_prompt_input_key
from langchain.schema import AIMessage, BaseMemory, BaseMessage, HumanMessage


class ChatMessageHistory(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)

    def add_user_message(self, message: str) -> None:
        self.messages.append(HumanMessage(content=message))

    def add_ai_message(self, message: str) -> None:
        self.messages.append(AIMessage(content=message))

    def clear(self) -> None:
        self.messages = []


class BaseChatMemory(BaseMemory, ABC):
    chat_memory: ChatMessageHistory = Field(default_factory=ChatMessageHistory)
    output_key: Optional[str] = None
    input_key: Optional[str] = None
    return_messages: bool = False

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key
        self.chat_memory.add_user_message(inputs[prompt_input_key])
        self.chat_memory.add_ai_message(outputs[output_key])

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()
'''

bot_suffix = f"I'm a bot that handles simple bugs and feature requests but I might make mistakes. Please be kind!"

def on_ticket(
    title: str, 
    summary: str, 
    issue_number: int, 
    issue_url: str, 
    username: str, 
    repo_full_name: str, 
    repo_description: str, 
    relevant_files: str = default_relevant_files
) -> bool:
    _org_name, repo_name = repo_full_name.split("/")
    subprocess.run('git config --global user.email "sweepai1248@gmail.com"'.split())
    subprocess.run('git config --global user.name "sweepaibot"'.split())

    # relevant_files = [] # TODO: fetch relevant files
    human_message = human_message_prompt.format(
        repo_name=repo_name, 
        issue_url=issue_url,
        username=username,
        repo_description=repo_description, 
        title=title, 
        description=summary, 
        relevant_directories=default_relevant_directories,
        relevant_files=relevant_files
    )
    chatGPT = ChatGPT()
    reply = chatGPT.chat(human_message)
    
    repo = g.get_repo(repo_full_name)
    issue = repo.get_issue(number=issue_number)
    issue.create_comment(reply + "\n\n---\n" + bot_suffix)

    parsed_files = []
    while not parsed_files:
        pr_code_response = chatGPT.chat(pr_code_prompt)
        # print(pr_code_response)
        if pr_code_response:
            files = pr_code_response.split('File: ')[1:]
            if not files:
                chatGPT.undo()
                continue
            while files[0] == '':
                files = files[1:]
            for file in files:
                if not file:
                    parsed_files = []
                    chatGPT.undo()
                    continue
                file_dict = re.search(file_regex, file, re.DOTALL)
                if file_dict is not None:
                    file_dict = {key: value.strip() for key, value in file_dict.groupdict().items()}
                    parsed_files.append(file_dict)
    pr_texts = {}
    while not pr_texts:
        pr_texts_response = chatGPT.chat(pr_text_prompt)
        pr_texts = re.search(pr_texts_regex, pr_texts_response, re.DOTALL)
        if pr_texts is not None:
            pr_texts = {key: value.strip() for key, value in pr_texts.groupdict().items()}
        else:
            chatGPT.undo()
    print("Got response!")
    pr_title = pr_texts["title"]
    summary = pr_texts["content"]

    issue_number = issue_url[issue_url.rfind("/"):]
    branch_name = make_valid_string(f"sweep/Issue_{issue_number}_{make_valid_string(title.strip())}").replace(' ', '_')[:250]
    base_branch = repo.get_branch(repo.default_branch)
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}",  base_branch.commit.sha)
    except Exception as e:
        print(f"Error: {e}")
        pass

    for file in parsed_files:
        file_path = file['filename']
        file_content = file['code']
        commit_message = f"sweep: {file['description'][:50]}"

        try:
            # check this is single file
            contents: ContentFile = repo.get_contents(file_path)
            repo.update_file(contents.path, commit_message, file_content, contents.sha, branch=branch_name)
        except GithubException:
            repo.create_file(file_path, commit_message, file_content, branch=branch_name)

    repo.create_pull(title=pr_title, body=summary, head=branch_name, base=repo.default_branch)
    return {"success": True}
