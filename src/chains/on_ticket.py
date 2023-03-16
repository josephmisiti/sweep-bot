"""
On Github ticket, get ChatGPT to deal with it
"""

import re
import requests
import os
import openai
import subprocess

from src.chains.on_ticket_prompts import system_message_prompt, human_message_prompt, file_format

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

response_regex = r'''(?P<reply>[\s\S]*)```(?P<implementation>[\s\S]*)```'''
file_regex = r'''(?P<filename>.*)Description: (?P<description>.*)\n"""\n(?P<code>.*)'''

# implementation = '''\
# """
# File: hello.py
# Description: abcdefg
# """
# print('Hello!')
# '''.strip()

def on_ticket(title: str, summary: str, relevant_files: str) -> bool:
    org_name = "sweepai"
    repo_name = "forked_langchain"
    username = "sweepaibot"
    repo_description = "Building applications with LLMs through composability"
    subprocess.run('git config --global user.email "sweepai1248@gmail.com"'.split())
    subprocess.run('git config --global user.name "sweepaibot"'.split())

    # relevant_files = [] # TODO: fetch relevant files
    system_message = system_message_prompt
    human_message = human_message_prompt.format(
        repo_name=repo_name, 
        repo_description=repo_description, 
        title=title, 
        description=summary, 
        # "\n\n".join([file_format.format(**file) for file in relevant_files]
        relevant_files=relevant_files
    )
    response_dict = {}
    while not response_dict:
        # response = mock_response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": human_message} 
            ],
            max_tokens=2048,
        ).choices[0].message["content"]
        print(response)
        print("Got response!")
        if response_dict := re.search(response_regex, response, re.DOTALL):
            response_dict = response_dict.groupdict()
    print("Accepted")
    response_dict = {key: value.strip() for key, value in response_dict.items()}
    reply = "A reply"
    pr_title = "A PR Title"
    summary = "A PR Summary"
    implementation = response_dict['implementation']
    files = implementation.split('"""\nFile: ')
    while files[0] == '':
        files = files[1:]
    subprocess.run(f'git clone https://{username}:{github_access_token}@github.com/{org_name}/{repo_name}.git'.split())
    os.chdir(repo_name)
    branch_name = "sweep/" + title.replace(' ', '_')
    branch_name = branch_name[:250]
    subprocess.run(f'git checkout -b {branch_name}'.split())
    for file in files:
        if not file:
            continue
        file_dict = re.search(file_regex, file, re.DOTALL).groupdict()
        file_dict = {key: value.strip() for key, value in file_dict.items()}
        with open(file_dict['filename'], 'w') as f:
            f.write(file_dict['code'])
        
        subprocess.run(f'git add {file_dict["filename"]}'.split())
        subprocess.run(['git', 'commit', '-m', f"sweep: {file_dict['description'][:50]}"])
    subprocess.run(f'git push -u origin {branch_name}'.split())
    url = f'https://api.github.com/repos/{org_name}/{repo_name}/pulls'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {github_access_token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    data = {
        'title': pr_title,
        'body': summary,
        'head': branch_name,
        'base': 'master',
    }
    subprocess.run(f'rm -rf {repo_name}/'.split())
    _response = requests.post(url, headers=headers, json=data)
    os.chdir("..")
    return True

example_title = "Add new memory called `ConversationTokenBufferMemory`"
example_comment = "Add new memory called ConversationTokenBufferMemory proposed in #1598. Closes #1598"
example_relevant_code = '''\

"""
File: langchain/chat_memory.py
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
'''

if  __name__ == "__main__":
    on_ticket(example_title, example_comment, example_relevant_code)