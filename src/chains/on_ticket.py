"""
On Github ticket, get ChatGPT to deal with it
"""

import re
import os
import openai
import subprocess

from loguru import logger
from github import Github, GithubException

from src.chains.on_ticket_models import ChatGPT, FileChange, PullRequest
from src.chains.on_ticket_prompts import (
    human_message_prompt,
    pr_code_prompt,
    pr_text_prompt,
)

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)


def make_valid_string(string: str):
    pattern = r"[^\w./-]+"
    return re.sub(pattern, " ", string)


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
File: langchain/memory/chat_memory.p
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

default_relevant_directories = ""
default_relevant_files = ""

bot_suffix = "I'm a bot that handles simple bugs and feature requests\
but I might make mistakes. Please be kind!"


def on_ticket(
    title: str,
    summary: str,
    issue_number: int,
    issue_url: str,
    username: str,
    repo_full_name: str,
    repo_description: str,
    relevant_files: str = default_relevant_files,
):
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
        relevant_files=relevant_files,
    )
    chatGPT = ChatGPT()
    reply = chatGPT.chat(human_message)

    repo = g.get_repo(repo_full_name)
    repo.get_issue(number=issue_number).create_comment(reply + "\n\n---\n" + bot_suffix)

    parsed_files: list[FileChange] = []
    while not parsed_files:
        pr_code_response = chatGPT.chat(pr_code_prompt)
        if pr_code_response:
            files = pr_code_response.split("File: ")[1:]
            while files and files[0] == "":
                files = files[1:]
            if not files:
                parsed_files = []
                chatGPT.undo()
                continue
            for file in files:
                try:
                    parsed_file = FileChange.from_string(file)
                    parsed_files.append(parsed_file)
                except Exception:
                    parsed_files = []
                    chatGPT.undo()
                    continue
    logger.info("Accepted ChatGPT result")

    pr_texts: PullRequest | None = None
    while pr_texts is None:
        pr_texts_response = chatGPT.chat(pr_text_prompt)
        try:
            pr_texts = PullRequest.from_string(pr_texts_response)
        except Exception:
            chatGPT.undo()

    branch_name = make_valid_string(
        f"sweep/Issue_{issue_number}_{make_valid_string(title.strip())}"
    ).replace(" ", "_")[:250]
    base_branch = repo.get_branch(repo.default_branch)
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
    except Exception as e:
        logger.error(f"Error: {e}")

    for file in parsed_files:
        commit_message = f"sweep: {file.description[:50]}"

        try:
            # TODO: check this is single file
            contents = repo.get_contents(file.filename)
            assert not isinstance(contents, list)
            repo.update_file(
                file.filename,
                commit_message,
                file.code,
                contents.sha,
                branch=branch_name,
            )
        except GithubException:
            repo.create_file(
                file.filename, commit_message, file.code, branch=branch_name
            )

    repo.create_pull(
        title=pr_texts.title,
        body=pr_texts.content,
        head=branch_name,
        base=repo.default_branch,
    )
    return {"success": True}
