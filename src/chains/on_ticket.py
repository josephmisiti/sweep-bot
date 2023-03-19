"""
On Github ticket, get ChatGPT to deal with it
"""

import os
import openai

from loguru import logger
from github import Github

from src.chains.on_ticket_models import (
    ChatGPT,
    FileChange,
    FileChangeRequest,
    FilesToChange,
    PullRequest,
)
from src.chains.on_ticket_prompts import (
    human_message_prompt,
    pr_text_prompt,
    files_to_change_prompt,
    create_file_prompt,
    modify_file_prompt,
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

    file_change_requests: list[FileChangeRequest] = []
    count = 0

    while not file_change_requests:
        count += 1
        logger.info(f"Generating for the {count}th time...")
        files_to_change_response = chatGPT.chat(files_to_change_prompt)
        try:
            files_to_change = FilesToChange.from_string(files_to_change_response)
            files_to_create: list[str] = files_to_change.files_to_create.split("*")
            files_to_modify: list[str] = files_to_change.files_to_modify.split("*")
            logger.debug(file_change_requests)
            for file_change_request, change_type in zip(
                files_to_create + files_to_modify,
                ["create"] * len(files_to_create) + ["modify"] * len(files_to_modify),
            ):
                file_change_request = file_change_request.strip()
                if not file_change_request or file_change_request == "None":
                    continue
                logger.debug(file_change_request, change_type)
                try:
                    file_change_requests.append(
                        FileChangeRequest.from_string(
                            file_change_request, change_type=change_type
                        )
                    )
                except Exception:
                    chatGPT.undo()
                    continue
        except Exception:
            chatGPT.undo()
            continue

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

    count = 0
    for file in file_change_requests:
        if file.change_type == "create":
            file_change = None
            while not file_change:
                create_file_response = chatGPT.chat(
                    create_file_prompt.format(
                        filename=file.filename,
                        instructions=file.instructions,
                    )
                )
                try:
                    file_change = FileChange.from_string(create_file_response)
                except Exception:
                    chatGPT.undo()
                    continue
            commit_message = f"sweep: {file_change.commit_message[:50]}"
            logger.debug(
                f"{file.filename}, {commit_message}, {file_change.code}, {branch_name}"
            )
            repo.create_file(
                file.filename, commit_message, file_change.code, branch=branch_name
            )
        elif file.change_type == "modify":
            contents = repo.get_contents(file.filename, ref=branch_name)
            file_change = None
            while not file_change:
                modify_file_response = chatGPT.chat(
                    modify_file_prompt.format(
                        filename=file.filename,
                        instructions=file.instructions,
                        code=contents.decoded_content.decode("utf-8"),
                    )
                )
                try:
                    file_change = FileChange.from_string(modify_file_response)
                except Exception:
                    chatGPT.undo()
                    continue
            commit_message = f"sweep: {file_change.commit_message[:50]}"
            repo.update_file(
                file.filename,
                commit_message,
                file_change.code,
                contents.sha,
                branch=branch_name,
            )
        else:
            raise Exception("Invalid change type")

    repo.create_pull(
        title=pull_request.title,
        body=pull_request.content,  # link back to issue
        head=branch_name,
        base=repo.default_branch,
    )

    logger.info("Done!")
    return {"success": True}
