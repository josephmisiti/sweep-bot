system_message_prompt = "You are an engineer assigned to the following Github ticket."

# system_message_prompt = '''You are an engineer assigned the following Github ticket. You can write your code based on the provided relevant code. 
# Answer in markdown format format (with triple ticks around code):
# ```
# """
# File: {filename_1}
# Description: {description_1}
# """
# {code_1}
# ```
# '''

human_message_prompt = '''
Repo: {repo_name}: {repo_description}
Username: {username}
Title: {title}
Description: {description}

Relevant Related Files:
```
{relevant_files}
```

Write a short response to this user, without writing long pieces of code.
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