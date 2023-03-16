system_message_prompt = '''You are an engineer assigned the following Github ticket. You can write your code based on the provided relevant code. 
Answer in markdown format format (with triple ticks around code):
```
"""
File: {filename_1}
Description: {description_1}
"""
{code_1}
```
'''

human_message_prompt = '''
Repo: {repo_name}: {repo_description}
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
"""
{code}
'''