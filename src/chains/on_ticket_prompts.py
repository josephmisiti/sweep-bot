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

files_to_change_prompt = """
Provide a list of files you would like to modify or create with brief instructions on what to modify, in few sentences. The list of files to create or modify may be empty: just leave the header with "* None". Format:

Thoughts: {thoughts}
Create:
* `{filename_1}`: {instructions_1}
* `{filename_2}`: {instructions_2}
Modify:
* `{filename_3}`: {instructions_3}
* `{filename_4}`: {instructions_4}
"""

create_file_prompt = """
Create the following file using the following instructions:

File Name: {filename}

Instructions: {instructions}

Reply in the following format:

Thoughts: {{thoughts}}
Commit Message: {{commit_message}}
```
{{new_code}}
```
"""

modify_file_prompt = """
Modify the following file using the following instructions:

File Name: {filename}
Old Code:
```
{code}
```

Instructions: {instructions}

Reply in the following format:

Thoughts: {{thoughts}}
Commit Message: {{commit_message}}
```
{{new_code}}
```
"""


# Make a pull request based on the contents of the ticket and the chat history.
# TODO: change to commit message
pr_code_prompt = '''
Make instructions for a pull request by listing the set of files you would like to add or modify. 
* To create a new file, set the filename to the path of the new file with instructions on how to code the new features. This should be done for new features.
* To modify an existing file, set the filename to the path of the existing file with instructions on what to add or remove from the code. This should be done for bug fixes.
Format:

File: {filename_1}
Description: {description_1}
"""
{instructions_1}
"""

File: {filename_2}
Description: {description_2}
"""
{instructions_2}
"""
'''

pr_text_prompt = """
Awesome! Could you also provide a PR message in the following format?

Title: {title}
Branch Name: {branch_name}
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

Changes Requested:
{changes_requested}

Write the new file.
"""
