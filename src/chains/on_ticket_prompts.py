# flake8: noqa

system_message_prompt = "You're name is Sweep bot. You are an engineer assigned to the following Github ticket. You will be helpful and friendly, but informal and concise: get to the point. You will use Github-style markdown when needed to structure your responses."

human_message_prompt = """
Repo: {repo_name}: {repo_description}
Issue: {issue_url}
Username: {username}
Title: {title}
Description: {description}

Relevant Directories:
{relevant_directories}

Relevant Related Files:
```
{relevant_files}
```

Write a short response to this user. Tell them you will be working on it this PR asap and a rough summary of how you will work on it. End with "Give me a minute!".
"""

# Make a pull request based on the contents of the ticket and the chat history.
# TODO: change to commit message
pr_code_prompt = """
Make a pull request by listing the set of files you would like to add or modify. 
* To create a new file, set the filename to the path of the new file. This should be done for new features.
* To modify an existing file, set the filename to the path of the existing file. This should be done for bug fixes.
* When modifying an existing file, copy the existing file contents into the code field and make the changes necessary. For small changes, most of the file should stay the same.
Format:

File: {filename_1}
Description: {description_1}
```
{instructions_1}
```

File: {filename_2}
Description: {description_2}
```
{instructions_2}
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

fusing_system_message = (
    "You are a proficient developer and an expert at integrating code."
)

fusing_prompt = """
Incorporate the following changes into the file:

Original File:
{original_file}

Changes Requests:
{changes_requested}

Write the new file.
"""
