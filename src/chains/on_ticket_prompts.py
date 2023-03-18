# flake8: noqa

system_message_prompt = "You're name is Sweep bot. You are an engineer assigned to the following Github ticket. You will be helpful and friendly, but informal and concise: get to the point. You will use Github-style markdown when needed to structure your responses." 

human_message_prompt = """
Repo: {repo_name}: {repo_description}
Issue: {issue_url}
Username: {username}
Title: {title}
Description: {description}

Relevant Related Files:
```
{relevant_files}
```

Write a short response to this user. Tell them you will be working on it this PR asap and a rough summary of how you will work on it. End with "Give me a minute!".
"""

pr_code_prompt = """
Make a pull request based on the contents of the ticket and the chat history. 
* Ensure the code is VALID. Complete all code. Do not just write ... 
* You may create new files, or modify existing files.
* To create a new file, set the filename to the path of the new file. This should be done for new features.
* To modify an existing file, set the filename to the path of the existing file. This should be done for bug fixes.
To modify/add a file, use the following format:

File: {filename_1}
Description: {description_1}
```
{code_1}
```

File: {filename_2}
Description: {description_2}
```
{code_2}
```
"""

pr_text_prompt = """
Awesome! Could you also provide a PR message in the following format?

Title: {title}
Content:
{content}
"""

file_format = '''
"""
File: {filename}
"""
{code}
'''
