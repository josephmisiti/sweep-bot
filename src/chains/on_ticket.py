"""
On Github ticket, get ChatGPT to deal with it
"""

import re
from dotenv import load_dotenv
load_dotenv()

import os
import openai
openai.api_key = os.environ.get("OPENAI_API_KEY")

system_message_prompt = '''
Given the following Github ticket and relevant code, write code and answer in the following format:

Reply: 
(thoughts on the potential problem, the potential solution, and implementation strategies, all in markdown)

Implementation:
```
"""
File: {filename_1}
Description: {description_1}
"""
{code_1}

"""
File: {filename_2}
Description: {description_2}
"""
{code_2}

...
```

PR Summary:
(PR Summary in markdown)
'''

human_message_prompt = '''
Title: {title}
Description: {description}

Relevant Related Files:
```
{relevant_files}
```
'''

file_format = '''
"""
File: {filename}
Description: {description}
"""
{code}
'''

response_regex = r'''Reply:(.*)Implementation:```(.*)```PR Summary:(.*)'''

def on_ticket(title: str, summary: str) -> bool:
    relevant_files = [] # TODO: Get relevant files
    system_message = system_message_prompt.format(relevant_files)
    human_message = human_message_prompt.format(title, summary, "\n\n".join([file_format.format(**file) for file in relevant_files]))
    response_dict = {}
    while not response_dict:
        response = openai.ChatCompletion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "message": system_message},
                {"role": "human", "message": human_message}
            ]
        )
        if response_dict := re.search(response_regex, response.choices[0].text, re.DOTALL):
            response_dict = response_dict.groupdict()
    response_dict = {key: value.strip() for key, value in response_dict.items()}
    # handle making reply
    # handle making PR
    return True


if  __name__ == "__main__":
    pass