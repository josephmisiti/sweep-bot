"""
On Github ticket, get ChatGPT to deal with it
"""

# TODO: Add file validation

import os
import openai

from loguru import logger
from github import Github

from src.core.prompts import system_message_prompt, human_message_prompt_comment
from src.core.sweep_bot import SweepBot
from src.utils.github_utils import get_relevant_directories, get_relevant_directories_remote

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)


def on_comment(
    repo_full_name: str,
    repo_description: str,
    branch_name: str,
    comment: str,
    path: str,
    pr_title: str,
    pr_body: str,
    pr_line_position: int,
):
    # Flow:
    # 1. Get relevant files
    # 2: Get human message
    # 3. Get files to change
    # 4. Get file changes
    # 5. Create PR
    logger.info(
        "Calling on_comment() with the following arguments: {comment}, {repo_full_name}, {repo_description}, {branch_name}, {path}",
        comment=comment,
        repo_full_name=repo_full_name,
        repo_description=repo_description,
        branch_name=branch_name,
        path=path,
        pr_title=pr_title,
        pr_body=pr_body,
    )
    _, repo_name = repo_full_name.split("/")

    logger.info("Getting repo {repo_full_name}", repo_full_name=repo_full_name)
    repo = g.get_repo(repo_full_name)
    src_contents = repo.get_contents("/", ref=branch_name)
    relevant_directories, relevant_files = get_relevant_directories(src_contents, repo)  # type: ignore
    # Gets the exact line that the comment happened on
    pr_file = (
        repo.get_contents(path, ref=branch_name)
        .decoded_content.decode("utf-8")
        .splitlines()
    )
    logger.info("PR File: {pr_file}", pr_file=pr_file)
    pr_line = pr_file[pr_line_position - 1]
    logger.info("PR Line: {pr_line}", pr_line=pr_line)
    # src_contents = repo.get_contents("src", ref=ref)
    # relevant_directories, relevant_files = get_relevant_directories_remote(title)  # type: ignore

    logger.info("Getting response from ChatGPT...")
    human_message = human_message_prompt_comment.format(
        repo_name=repo_name,
        repo_description=repo_description,
        comment=comment,
        path=path,
        relevant_directories=relevant_directories,
        relevant_files=relevant_files,
        pr_title=pr_title,
        pr_body=pr_body,
        pr_line=pr_line,
    )

    sweep_bot = SweepBot.from_system_message_content(
        system_message_prompt + "\n\n" + human_message, model="gpt-3.5-turbo", repo=repo
    )

    logger.info("Fetching files to modify/create...")
    file_change_requests = sweep_bot.get_files_to_change()

    logger.info("Making Code Changes...")
    sweep_bot.change_files_in_github(file_change_requests, branch_name)

    logger.info("Done!")
    return {"success": True}
