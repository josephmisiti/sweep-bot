"""
On Github ticket, get ChatGPT to deal with it
"""

import re
import os
import openai

from loguru import logger
from github import Github, UnknownObjectException

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

github_access_token = os.environ.get("GITHUB_TOKEN")
openai.api_key = os.environ.get("OPENAI_API_KEY")

g = Github(github_access_token)


def make_valid_string(string: str):
    pattern = r"[^\w./-]+"
    return re.sub(pattern, " ", string)


default_relevant_directories = ""
default_relevant_files = ""

bot_suffix = "I'm a bot that handles simple bugs and feature requests but I might make mistakes. Please be kind!"


def get_relevant_directories(src_contents: list, repo) -> tuple[str, str]:
    # Initialize the relevant directories string
    relevant_directories = ""
    relevant_files = '"""'

    # Iterate over the contents of the src folder
    for content in src_contents:
        if content.type == "dir":
            # If the content is a directory, append the directory name to the
            # relevant directories string
            # If the content is a directory, append the directory name to the
            # relevant directories string
            relevant_directories += content.path.replace("src/", "") + "\n"

            # Get the contents of the directory
            dir_contents = repo.get_contents(content.path)

            # Iterate over the contents of the directory
            for file in dir_contents:
                if file.type == "file":
                    # If the content is a file, append the file name to the
                    # relevant directories string with an indentation of 4 spaces
                    relevant_directories += "    " + file.name + "\n"

                    if file.name.endswith(".py") and file.name == "api.py":
                        # If the content is a Python file, append the
                        # file path to the relevant files string
                        relevant_files += f'\nFile: {file.path}\n"""'

                        # Get the contents of the file
                        file_contents = repo.get_contents(file.path)
                        # Decode the contents of the file from base64 and append
                        # it to the relevant files string
                        relevant_files += (
                            f'"""\n{file_contents.decoded_content.decode("utf-8")}\n"""'
                        )

    # Print the relevant directories and files strings
    return relevant_directories, relevant_files


def on_ticket(
    title: str,
    summary: str,
    issue_number: int,
    issue_url: str,
    username: str,
    repo_full_name: str,
    repo_description: str,
    relevant_files: str = default_relevant_files,
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
    src_contents = repo.get_contents("src")
    relevant_directories, relevant_files = get_relevant_directories(src_contents, repo)  # type: ignore

    logger.info("Getting response from ChatGPT...")
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
    chatGPT = ChatGPT(model="gpt-3.5-turbo")
    reply = chatGPT.chat(human_message)

    logger.info("Sending response...")
    repo.get_issue(number=issue_number).create_comment(reply + "\n\n---\n" + bot_suffix)

    # TODO: abstractify this process

    logger.info("Fetching files to modify/create...")

    files_to_modify: list[FileChangeRequest] = []
    files_to_create: list[FileChangeRequest] = []
    count = 0

    while not files_to_modify or not files_to_create:
        count += 1
        logger.info(f"Generating for the {count}th time...")
        files_to_change_response = chatGPT.chat(files_to_change_prompt)
        try:
            files_to_change = FilesToChange.from_string(files_to_change_response)
            if (
                files_to_change.files_to_modify is None
                and files_to_change.files_to_create is None  # noqa: W503
            ):
                continue
            if files_to_change.files_to_modify is None:
                files_to_change.files_to_modify = ""
            if files_to_change.files_to_create is None:
                files_to_change.files_to_create = ""
            for file_change_request in files_to_change.files_to_modify.split("*"):
                file_change_request = file_change_request.strip()
                if not file_change_request:
                    continue
                try:
                    files_to_modify.append(
                        FileChangeRequest.from_string(file_change_request)
                    )
                except Exception:
                    chatGPT.undo()
                    continue
            for file_change_request in files_to_change.files_to_create.split("*"):
                file_change_request = file_change_request.strip()
                if not file_change_request:
                    continue
                try:
                    files_to_create.append(
                        FileChangeRequest.from_string(file_change_request)
                    )
                except Exception:
                    chatGPT.undo()
                    continue
        except Exception:
            chatGPT.undo()
            continue

    logger.info("Generating PR...")
    pull_request = None
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
    branch_name = "sweep/" + pull_request.branch_name[:250]
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
    except Exception as e:
        logger.error(f"Error: {e}")
    repo.create_pull(
        title=pull_request.title,
        body=pull_request.content,
        head=branch_name,
        base=repo.default_branch,
    )

    for file in files_to_create:
        # Can be made async
        commit_message = f"sweep: {file.commit_message[:50]}"
        file_change = None
        while not file_change:
            modify_file_response = chatGPT.chat(
                modify_file_prompt.format(
                    filename=file.filename,
                    instructions=file.instructions,
                )
            )
            try:
                file_change = FileChange.from_string(modify_file_response)
            except Exception:
                chatGPT.undo()
                continue

        try:
            # TODO: check this is single file
            contents = repo.get_contents(file.filename)
            repo.update_file(
                file.filename,
                commit_message,
                file_change.code,
                contents.sha,
                branch=branch_name,
            )
        except UnknownObjectException:
            repo.create_file(
                file.filename, commit_message, file.code, branch=branch_name
            )

    for file in files_to_modify:
        # Can be made async
        commit_message = f"sweep: {file.commit_message[:50]}"
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

        try:
            # TODO: check this is single file
            contents = repo.get_contents(file.filename)
            repo.update_file(
                file.filename,
                commit_message,
                file_change.code,
                contents.sha,
                branch=branch_name,
            )
        except UnknownObjectException:
            repo.create_file(
                file.filename, commit_message, file.code, branch=branch_name
            )

    # logger.info("Generating code...")
    # parsed_files: list[FileChange] = []
    # count = 0
    # while not parsed_files:
    #     count += 1
    #     logger.info(f"Generating for the {count}th time...")
    #     pr_code_response = chatGPT.chat(pr_code_prompt)
    #     if pr_code_response:
    #         files = pr_code_response.split("File: ")[1:]
    #         while files and files[0] == "":
    #             files = files[1:]
    #         if not files:
    #             # TODO(wzeng): Fuse changes back using GPT4
    #             parsed_files = []
    #             chatGPT.undo()
    #             continue
    #         for file in files:
    #             try:
    #                 parsed_file = FileChange.from_string(file)
    #                 parsed_files.append(parsed_file)
    #             except Exception:
    #                 parsed_files = []
    #                 chatGPT.undo()
    #                 continue

    # logger.info("Generating PR summary and text...")
    # pr_texts: PullRequest | None = None
    # count = 0
    # while pr_texts is None:
    #     count += 1
    #     logger.info(f"Generating for the {count}th time...")
    #     pr_texts_response = chatGPT.chat(pr_text_prompt)
    #     try:
    #         pr_texts = PullRequest.from_string(pr_texts_response)
    #     except Exception:
    #         chatGPT.undo()

    # branch_name = make_valid_string(
    #     f"sweep/Issue_{issue_number}_{make_valid_string(title.strip())}"
    # ).replace(" ", "_")[:250]
    # base_branch = repo.get_branch(repo.default_branch)
    # try:
    #     repo.create_git_ref(f"refs/heads/{branch_name}", base_branch.commit.sha)
    # except Exception as e:
    #     logger.error(f"Error: {e}")

    # # code_fuser = ChatGPT(messages=[Message(role="system", content=fusing_system_message)], model="gpt-3.5-turbo")
    # code_fuser = ChatGPT(
    #     messages=[Message(role="system", content=fusing_system_message)], model="gpt-4"
    # )
    # for file in parsed_files:
    #     # Can be made async
    #     commit_message = f"sweep: {file.description[:50]}"

    #     try:
    #         # TODO: check this is single file
    #         contents = repo.get_contents(file.filename)
    #         assert not isinstance(contents, list)
    #         new_contents = code_fuser.chat(
    #             fusing_prompt.format(
    #                 original_file=contents.decoded_content.decode("utf-8"),
    #                 changes_requested=file.code,
    #             )
    #         )
    #         code_fuser.undo()
    #         if "```" in new_contents:
    #             match = re.search(r"```(.*)```", new_contents, re.DOTALL)
    #             if match is not None:
    #                 new_contents = match.group(1)

    #         repo.update_file(
    #             file.filename,
    #             commit_message,
    #             new_contents,
    #             # file.code,
    #             contents.sha,
    #             branch=branch_name,
    #         )
    #     except UnknownObjectException:
    #         repo.create_file(
    #             file.filename, commit_message, file.code, branch=branch_name
    #         )

    return {"success": True}
