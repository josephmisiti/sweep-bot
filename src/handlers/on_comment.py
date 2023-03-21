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
from src.utils.github_utils import get_relevant_directories

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)

bot_suffix = "I'm a bot that handles simple bugs and feature requests\
but I might make mistakes. Please be kind!"


def on_comment(
    repo_full_name: str,
    repo_description: str,
    branch_name: str,
    comment: str,
    path: str,
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
    )
    _, repo_name = repo_full_name.split("/")

    logger.info("Getting repo {repo_full_name}", repo_full_name=repo_full_name)
    repo = g.get_repo(repo_full_name)
    src_contents = repo.get_contents("/")
    relevant_directories, relevant_files = get_relevant_directories(src_contents, repo)  # type: ignore

    logger.info("Getting response from ChatGPT...")
    human_message = human_message_prompt_comment.format(
        repo_name=repo_name,
        repo_description=repo_description,
        comment=comment,
        path=path,
        relevant_directories=relevant_directories,
        relevant_files=relevant_files,
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
