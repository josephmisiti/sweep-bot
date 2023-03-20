"""
On Github ticket, get ChatGPT to deal with it
"""

import os
import openai

from loguru import logger
from github import Github

from src.chains.on_ticket_models import (
    ChatGPT,
    PullRequest,
)
from src.chains.on_ticket_prompts import (
    human_message_prompt,
    pr_text_prompt,
)
from src.utils.code_utils import commit_files_to_github, get_files_from_chatgpt
from src.utils.github_utils import get_relevant_directories, make_valid_string

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)

bot_suffix = "I'm a bot that handles simple bugs and feature requests\
but I might make mistakes. Please be kind!"


# Flow:
# 1. Get relevant files
# 2: Get human message
# 3. Get files to change
# 4. Get file changes
# 5. Create PR
def on_ticket(
    title: str,
    summary: str,
    issue_number: int,
    issue_url: str,
    username: str,
    repo_full_name: str,
    repo_description: str,
    relevant_files: str = "",
):
    logger.info(
        "Calling on_ticket() with the following arguments: {title}, {summary}, {issue_number}, {issue_url}, {username}, {repo_full_name}, {repo_description}, {relevant_files}",
        title=title,
        summary=summary,
        issue_number=issue_number,
        issue_url=issue_url,
        username=username,
        repo_full_name=repo_full_name,
        repo_description=repo_description,
        relevant_files=relevant_files,
    )
    _org_name, repo_name = repo_full_name.split("/")

    logger.info("Getting repo {repo_full_name}", repo_full_name=repo_full_name)
    repo = g.get_repo(repo_full_name)
    src_contents = repo.get_contents("/")
    relevant_directories, relevant_files = get_relevant_directories(src_contents, repo)  # type: ignore

    logger.info("Getting response from ChatGPT...")
    human_message = human_message_prompt.format(
        repo_name=repo_name,
        issue_url=issue_url,
        username=username,
        repo_description=repo_description,
        title=title,
        description=summary,
        relevant_directories=relevant_directories,
        relevant_files=relevant_files,
    )
    chatGPT = ChatGPT(model="gpt-3.5-turbo")
    reply = chatGPT.chat(human_message)

    logger.info("Sending response...")
    repo.get_issue(number=issue_number).create_comment(reply + "\n\n---\n" + bot_suffix)

    # TODO: abstractify this process

    logger.info("Fetching files to modify/create...")

    file_change_requests = get_files_from_chatgpt(chatGPT=chatGPT)

    logger.info("Generating PR...")
    pull_request = None
    count = 0
    while not pull_request:
        count += 1
        logger.info(f"Generating for the {count}th time...")
        pr_text_response = chatGPT.chat(pr_text_prompt)
        try:
            pull_request = PullRequest.from_string(pr_text_response)
        except Exception:
            chatGPT.undo()
            continue

    logger.info("Making PR...")
    base_branch = repo.get_branch(repo.default_branch)
    branch_name = make_valid_string("sweep/" + pull_request.branch_name[:250])
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
    except Exception as e:
        logger.error(f"Error: {e}")

    commit_files_to_github(
        file_change_requests=file_change_requests,
        repo=repo,
        chatGPT=chatGPT,
        branch_name=branch_name,
    )

    repo.create_pull(
        title=pull_request.title,
        body=pull_request.content,  # link back to issue
        head=branch_name,
        base=repo.default_branch,
    )

    logger.info("Done!")
    return {"success": True}
