system_message_prompt = '''You are an engineer assigned the following Github ticket. You can write your code based on the provided relevant code. Make as many new files as needed but multiple files are not necessarily required. Answer in the following format:

(response on: the potential problem (if any), the potential solution, and implementation strategies, all in markdown)

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

PR Title: {title}
PR Summary:
(PR Summary in markdown)
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