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

call_openai_title = lambda text: openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Come up with a pull request title for these changes:\n{text}\n\nPull Request Title:"} 
    ],
    max_tokens=2048,
).choices[0].message["content"]

call_openai_summary = lambda text: openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Come up with a pull request summary for these changes:\n{text}\n\nPull Request Summary:"} 
    ],
    max_tokens=2048,
).choices[0].message["content"]


call_openai_reply = lambda text: openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Come up with a pull request reply for this description:\n{text}\n\nPull Request Reply:"} 
    ],
    max_tokens=2048,
).choices[0].message["content"]

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
    reply = call_openai_reply(title + summary)
    implementation = response_dict['implementation']
    pr_title = call_openai_title(implementation).lower()
    summary = call_openai_summary(implementation).lower()
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
    _response = requests.post(url, headers=headers, json=data)
    os.chdir("..")
    subprocess.run(f'rm -rf {repo_name}/'.split())
    return True