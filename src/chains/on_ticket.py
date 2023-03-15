"""
On Github ticket, get ChatGPT to deal with it
"""

import re
from dotenv import load_dotenv
load_dotenv()

import requests
import os
import openai
import subprocess
github_access_token = os.environ.get("GITHUB_ACCESS_TOKEN")
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

response_regex = r'''Reply:(?P<reply>.*)Implementation:```(?P<implementation>.*)```PR Summary:(?P<summary>.*)'''
file_regex = r'''(?P<filename>.*)Description: (?P<description>.*)\n"""\n(?P<code>.*)'''

def on_ticket(title: str, summary: str) -> bool:
    # relevant_files = [] # TODO: Get relevant files
    # system_message = system_message_prompt.format(relevant_files)
    # human_message = human_message_prompt.format(title, summary, "\n\n".join([file_format.format(**file) for file in relevant_files]))
    # response_dict = {}
    # while not response_dict:
    #     response = openai.ChatCompletion(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "message": system_message},
    #             {"role": "human", "message": human_message}
    #         ]
    #     )
    #     if response_dict := re.search(response_regex, response.choices[0].text, re.DOTALL):
    #         response_dict = response_dict.groupdict()
    # response_dict = {key: value.strip() for key, value in response_dict.items()}
    # handle making reply
    # handle making PR
    # implementation = response_dict['implementation']
    implementation = '''\
"""
File: hello.py
Description: abcdefg
"""
print('Hello!')
'''.strip()
    files = implementation.split('"""\nFile: ')
    while files[0] == '':
        files = files[1:]
    subprocess.run(f'git clone https://wwzeng1:{github_access_token}@github.com/sweepai/forked_langchain.git'.split())
    os.chdir('forked_langchain')
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
    url = 'https://api.github.com/repos/sweepai/forked_langchain/pulls'
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {github_access_token}',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    data = {
        'title': 'Amazing new feature',
        'body': 'Please pull these awesome changes in!',
        'head': branch_name,
        'base': 'master',
    }
    subprocess.run('rm -rf forked_langchain/'.split())
    response = requests.post(url, headers=headers, json=data)
    return True


if  __name__ == "__main__":
    on_ticket("Hello world", "Hello world")
    pass