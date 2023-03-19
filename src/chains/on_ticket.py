"""
On Github ticket, get ChatGPT to deal with it
"""

import os
import openai

from loguru import logger
from github import Github, UnknownObjectException

from src.chains.on_ticket_models import ChatGPT, FileChange, PullRequest
from src.chains.on_ticket_prompts import (
    human_message_prompt,
    pr_code_prompt,
    pr_text_prompt,
)
from src.utils.github_utils import get_relevant_directories, make_valid_string

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)

bot_suffix = "I'm a bot that handles simple bugs and feature requests\
but I might make mistakes. Please be kind!"


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
    _, repo_name = repo_full_name.split("/")

    repo = g.get_repo(repo_full_name)
    src_contents = repo.get_contents("src")
    relevant_directories, relevant_files = get_relevant_directories(src_contents, repo)

    # relevant_files = [] # TODO: fetch relevant files
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
    chatGPT = ChatGPT()
    reply = chatGPT.chat(human_message)

    repo.get_issue(number=issue_number).create_comment(reply + "\n\n---\n" + bot_suffix)

    parsed_files: list[FileChange] = []
    while not parsed_files:
        pr_code_response = chatGPT.chat(pr_code_prompt)
        if pr_code_response:
            files = pr_code_response.split("File: ")[1:]
            while files and files[0] == "":
                files = files[1:]
            if not files:
                # TODO(wzeng): Fuse changes back using GPT4
                parsed_files = []
                chatGPT.undo()
                continue
            for file in files:
                try:
                    parsed_file = FileChange.from_string(file)
                    parsed_files.append(parsed_file)
                except Exception:
                    parsed_files = []
                    chatGPT.undo()
                    continue
    logger.info("Accepted ChatGPT result")

    pr_texts: PullRequest | None = None
    while pr_texts is None:
        pr_texts_response = chatGPT.chat(pr_text_prompt)
        try:
            pr_texts = PullRequest.from_string(pr_texts_response)
        except Exception:
            chatGPT.undo()

    branch_name = make_valid_string(
        f"sweep/Issue_{issue_number}_{make_valid_string(title.strip())}"
    ).replace(" ", "_")[:250]
    base_branch = repo.get_branch(repo.default_branch)
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
    except Exception as e:
        logger.error(f"Error: {e}")

    for file in parsed_files:
        commit_message = f"sweep: {file.description[:50]}"

        try:
            # TODO: check this is single file
            contents = repo.get_contents(file.filename)
            assert not isinstance(contents, list)
            repo.update_file(
                file.filename,
                commit_message,
                file.code,
                contents.sha,
                branch=branch_name,
            )
        except UnknownObjectException:
            repo.create_file(
                file.filename, commit_message, file.code, branch=branch_name
            )

    repo.create_pull(
        title=pr_texts.title,
        body=pr_texts.content,
        head=branch_name,
        base=repo.default_branch,
    )
    return {"success": True}
