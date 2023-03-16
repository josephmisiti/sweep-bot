"""
On Github ticket, get ChatGPT to deal with it
"""

import re
import requests
import os
import openai
import subprocess

from src.chains.on_ticket_prompts import system_message_prompt, human_message_prompt, file_format

# mock_response = """Reply:\nThe addition of a new memory named `ConversationTokenBufferMemory` seems to be for storing long conversations that exceed the threshold of the existing `ConversationSummaryBufferMemory`. This new memory uses LSTM-Based summarization model, which will summarize the conversation after it exceeds the maximum allowable tokens to keep the longer conversations. The proposal of this new memory can help in conversation storage and making a conclusion/summary of long discussions. \nAn important aspect for implementation is testing its workings across multiple use cases to ensure its effectiveness. Additionally, existing conversation storing and summarizing methods need to be examined and tested alongside `ConversationTokenBufferMemory`. \n\nImplementation:\n```\n\"\"\"\nFile: langchain/langchain/chat_memory.py\n\"\"\"\n\nfrom abc import ABC\nfrom typing import Any, Dict, List, Optional\n\nfrom pydantic import BaseModel, Field\n\nfrom langchain.memory.utils import get_prompt_input_key\nfrom langchain.schema import AIMessage, BaseMemory, BaseMessage, HumanMessage\n\n\nclass ChatMessageHistory(BaseModel):\n    messages: List[BaseMessage] = Field(default_factory=list)\n\n    def add_user_message(self, message: str) -> None:\n        self.messages.append(HumanMessage(content=message))\n\n    def add_ai_message(self, message: str) -> None:\n        self.messages.append(AIMessage(content=message))\n\n    def clear(self) -> None:\n        self.messages = []\n\n\nclass BaseChatMemory(BaseMemory, ABC):\n    chat_memory: ChatMessageHistory = Field(default_factory=ChatMessageHistory)\n    output_key: Optional[str] = None\n    input_key: Optional[str] = None\n    return_messages: bool = False\n\n    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:\n        \"\"\"Save context from this conversation to buffer.\"\"\"\n        if self.input_key is None:\n            prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)\n        else:\n            prompt_input_key = self.input_key\n        if self.output_key is None:\n            if len(outputs) != 1:\n                raise ValueError(f\"One output key expected, got {outputs.keys()}\")\n            output_key = list(outputs.keys())[0]\n        else:\n            output_key = self.output_key\n        self.chat_memory.add_user_message(inputs[prompt_input_key])\n        self.chat_memory.add_ai_message(outputs[output_key])\n\n    def clear(self) -> None:\n        \"\"\"Clear memory contents.\"\"\"\n        self.chat_memory.clear()\n\n\"\"\"\nFile: langchain/langchain/memory/summary_buffer.py\n\"\"\"\n\nfrom typing import Any, Dict, List\n\nfrom pydantic import BaseModel, root_validator\n\nfrom langchain.memory.chat_memory import BaseChatMemory\nfrom langchain.memory.summary import SummarizerMixin, LSTMTokenSummarizer\nfrom langchain.memory.utils import get_buffer_string\nfrom langchain.schema import BaseMessage, SystemMessage\n\n\nclass ConversationSummaryBufferMemory(BaseChatMemory, SummarizerMixin, BaseModel):\n    \"\"\"Buffer with summarizer for storing conversation memory.\"\"\"\n\n    max_token_limit: int = 2000\n    moving_summary_buffer: str = \"\"\n    memory_key: str = \"history\"\n\n    @property\n    def buffer(self) -> List[BaseMessage]:\n        return self.chat_memory.messages\n\n    @property\n    def memory_variables(self) -> List[str]:\n        \"\"\"Will always return list of memory variables.\n        :meta private:\n        \"\"\"\n        return [self.memory_key]\n\n    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:\n        \"\"\"Return history buffer.\"\"\"\n        buffer = self.buffer\n        if self.moving_summary_buffer != \"\":\n            first_messages: List[BaseMessage] = [\n                SystemMessage(content=self.moving_summary_buffer)\n            ]\n            buffer = first_messages + buffer\n        if self.return_messages:\n            final_buffer: Any = buffer\n        else:\n            final_buffer = get_buffer_string(\n                buffer, human_prefix=self.human_prefix, ai_prefix=self.ai_prefix\n            )\n        return {self.memory_key: final_buffer}\n\n    @root_validator()\n    def validate_prompt_input_variables(cls, values: Dict) -> Dict:\n        \"\"\"Validate that prompt input variables are consistent.\"\"\"\n        prompt_variables = values[\"prompt\"].input_variables\n        expected_keys = {\"summary\", \"new_lines\"}\n        if expected_keys != set(prompt_variables):\n            raise ValueError(\n                \"Got unexpected prompt input variables. The prompt expects \"\n                f\"{prompt_variables}, but it should have {expected_keys}.\"\n            )\n        return values\n\n    def get_num_tokens_list(self, arr: List[BaseMessage]) -> List[int]:\n        \"\"\"Get list of number of tokens in each string in the input array.\"\"\"\n        return [self.llm.get_num_tokens(get_buffer_string([x])) for x in arr]\n\n    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:\n        \"\"\"Save context from this conversation to buffer.\"\"\"\n        super().save_context(inputs, outputs)\n        # Prune buffer if it exceeds max token limit\n        buffer = self.chat_memory.messages\n        curr_buffer_length = sum(self.get_num_tokens_list(buffer))\n        if curr_buffer_length > self.max_token_limit:\n            pruned_memory = []\n            while curr_buffer_length > self.max_token_limit:\n                pruned_memory.append(buffer.pop(0))\n                curr_buffer_length = sum(self.get_num_tokens_list(buffer))\n            if self.moving_summary_buffer == \"\":\n                summary = self.predict_new_summary(pruned_memory, \"\")\n            else:\n                summary = LSTMTokenSummarizer().predict_new_summary(\n                    pruned_memory, self.moving_summary_buffer\n                )\n            self.chat_memory.clear()\n            self.chat_memory.messages += [SystemMessage(content=summary)]\n            self.moving_summary_buffer = summary\n\n    def clear(self) -> None:\n        \"\"\"Clear memory contents.\"\"\"\n        super().clear()\n        self.moving_summary_buffer = \"\"\n\nclass ConversationTokenBufferMemory(BaseChatMemory, SummarizerMixin, BaseModel):\n    \"\"\"\n    Buffer with LSTM summarization for very long texts\n    \"\"\"\n    max_token_limit: int = 20000\n    moving_summary_buffer: str = \"\"\n    memory_key: str = \"history\"\n\n    @property\n    def buffer(self) -> List[BaseMessage]:\n        return self.chat_memory.messages\n\n    @property\n    def memory_variables(self) -> List[str]:\n        return [self.memory_key]\n\n    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:\n        buffer = self.buffer\n        if self.moving_summary_buffer != \"\":\n            first_messages: List[BaseMessage] = [\n                SystemMessage(content=self.moving_summary_buffer)\n            ]\n            buffer = first_messages + buffer\n        if self.return_messages:\n            final_buffer: Any = buffer\n        else:\n            final_buffer = get_buffer_string(\n                buffer, human_prefix=self.human_prefix, ai_prefix=self.ai_prefix\n            )\n        return {self.memory_key: final_buffer}\n\n    def get_num_tokens_list(self, arr: List[BaseMessage]) -> List[int]:\n        return [self.llm.get_num_tokens(get_buffer_string([x])) for x in arr]\n\n    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:\n        super().save_context(inputs, outputs)\n        curr_buffer_length = sum(self.get_num_tokens_list(self.buffer))\n        if curr_buffer_length > self.max_token_limit:\n            pruned_memory = []\n            while curr_buffer_length > self.max_token_limit:\n                pruned_memory.append(self.buffer.pop(0))\n                curr_buffer_length = sum(self.get_num_tokens_list(self.buffer))\n            if self.moving_summary_buffer == \"\":\n                summary = LSTMTokenSummarizer().predict_new_summary(\n                    pruned_memory, \"\"\n                )\n            else:\n                summary = LSTMTokenSummarizer().predict_new_summary(\n                    pruned_memory, self.moving_summary_buffer\n                )\n\n            self.moving_summary_buffer = summary\n            self.chat_memory.messages += [SystemMessage(content=summary)]\n\n    def clear(self) -> None:\n        super().clear()\n        self.moving_summary_buffer = \"\"\n\n\n```\n\nPR Title: Add ConversationTokenBufferMemory Memory\nPR Summary: This PR adds a new memory called ConversationTokenBufferMemory. It is proposed to store long conversations that exceed the max token limit of 2000 stored in ConversationSummaryBufferMemory. To summarise long conversations, the LSTM-Based summarization model is used. This can help to store a longer conversation and make a conclusion/summary from long discussions. This PR updates the existing files `langchain/langchain/chat_memory.py` and `langchain/langchain/memory/summary_buffer.py`"""
mock_response = '''Issue: Add new memory called `ConversationTokenBufferMemory`

Current Situation:
The issue is to add a new memory called `ConversationTokenBufferMemory`. The relevant files are `ChatMessageHistory` code and a buffer memory summary code.

Potential Solutions:
There are certain ways to add `ConversationTokenBufferMemory`. One way can be to create a new class `ConversationTokenBufferMemory` that inherits the `BaseChatMemory`, which inherits from `ChatMessageHistory`. In the same way, it inherits from the `SummarizerMixin` and `BaseModel`. Its code could include:
```
from typing import Any, Dict, List

from pydantic import BaseModel

from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.summary_buffer import SummarizerMixin
from langchain.memory.utils import get_prompt_input_key
from langchain.schema import AIMessage, BaseMessage, HumanMessage


class ConversationTokenBufferMemory(BaseChatMemory, SummarizerMixin, BaseModel):
    """Buffer with summarizer for storing conversation memory."""
    
    memory_key = "convo"
    max_token_limit = 2000
    moving_summary_buffer = ""

    @property
    def buffer(self) -> List[BaseMessage]:
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables."""
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

        # Prune buffer if it exceeds max token limit
        buffer = self.chat_memory.messages
        curr_buffer_length = sum(get_num_tokens_list(buffer, self.llm))
        if curr_buffer_length > self.max_token_limit:
            pruned_memory = []
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = sum(get_num_tokens_list(buffer, self.llm))
            self.moving_summary_buffer = self.predict_new_summary(
                pruned_memory, self.moving_summary_buffer
            )

    def clear(self) -> None:
        """Clear memory contents."""
        super().clear()
        self.moving_summary_buffer = ""
```
Another solution can be to adjust the `ConversationSummaryBufferMemory` code so that it fits the new requirements.

Implementation:
```
"""
File: langchain/memory/conversation_token_buffer.py
Description: Code for “Conversation Token Buffer Memory”.
"""
from typing import Any, Dict, List

from pydantic import BaseModel

from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.summary_buffer import SummarizerMixin
from langchain.memory.utils import get_prompt_input_key
from langchain.schema import AIMessage, BaseMessage, HumanMessage


class ConversationTokenBufferMemory(BaseChatMemory, SummarizerMixin, BaseModel):
    """Buffer with summarizer for storing conversation memory."""
    
    memory_key = "convo"
    max_token_limit = 2000
    moving_summary_buffer = ""

    @property
    def buffer(self) -> List[BaseMessage]:
        return self.chat_memory.messages

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables."""
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

        # Prune buffer if it exceeds max token limit
        buffer = self.chat_memory.messages
        curr_buffer_length = sum(get_num_tokens_list(buffer, self.llm))
        if curr_buffer_length > self.max_token_limit:
            pruned_memory = []
            while curr_buffer_length > self.max_token_limit:
                pruned_memory.append(buffer.pop(0))
                curr_buffer_length = sum(get_num_tokens_list(buffer, self.llm))
            self.moving_summary_buffer = self.predict_new_summary(
                pruned_memory, self.moving_summary_buffer
            )

    def clear(self) -> None:
        """Clear memory contents."""
        super().clear()
        self.moving_summary_buffer = ""
```
PR Title: Added new memory called `ConversationTokenBufferMemory`
PR Summary: 
Added a new memory called `ConversationTokenBufferMemory`, which extends the `BaseChatMemory` to be able to store tokens of a given conversation.'''

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

response_regex = r'''(?P<reply>.*)```(?P<implementation>.*)```\n*PR Title:(?P<title>.*)PR Summary:(?P<summary>.*)'''
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
    reply = response_dict["reply"]
    pr_title = response_dict["title"]
    summary = response_dict["summary"]
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