system_message_prompt = "You're name is Sweep bot. You are an engineer assigned to the following Github ticket."

human_message_prompt = '''
Repo: {repo_name}: {repo_description}
Username: {username}
Title: {title}
Description: {description}

Relevant Related Files:
```
{relevant_files}
```

Write a short response to this user, telling them you will be working on it this PR asap and a rough summary of how you will work on it. End with "Give me a minute!".
'''

pr_code_prompt = '''
Please make a pull request based on the contents of the ticket and the chat history in the following format (generate as many files as needed but multiple files is not necessarily required):

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
'''

pr_text_prompt = '''
Awesome! Could you also provide a PR message in the following format?

Title: {title}
Content:
{content}
'''

file_format = '''
"""
File: {filename}
"""
{code}
'''