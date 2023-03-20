from github import Repository

from loguru import logger
from src.common.models import (
    ChatGPT,
    RegexMatchError,
    FileChange,
    FileChangeRequest,
    FilesToChange,
    PullRequest,
)
from src.common.prompts import (
    files_to_change_prompt,
    create_file_prompt,
    modify_file_prompt,
    pull_request_prompt,
)


def get_files_from_chatgpt(chatGPT: ChatGPT):
    file_change_requests: list[FileChangeRequest] = []
    for count in range(5):
        if file_change_requests:
            return file_change_requests
        try:
            logger.info(f"Generating for the {count}th time...")
            files_to_change_response = chatGPT.chat(files_to_change_prompt)
            files_to_change = FilesToChange.from_string(files_to_change_response)
            files_to_create: list[str] = files_to_change.files_to_create.split("*")
            files_to_modify: list[str] = files_to_change.files_to_modify.split("*")
            logger.debug(files_to_change)
            for file_change_request, change_type in zip(
                files_to_create + files_to_modify,
                ["create"] * len(files_to_create) + ["modify"] * len(files_to_modify),
            ):
                file_change_request = file_change_request.strip()
                if not file_change_request or file_change_request == "None":
                    continue
                logger.debug(file_change_request, change_type)
                file_change_requests.append(
                    FileChangeRequest.from_string(
                        file_change_request, change_type=change_type
                    )
                )
        except RegexMatchError:
            logger.warning("Failed to parse! Retrying...")
            chatGPT.undo()
            continue
    raise Exception("Could not generate files to change")


def generate_pull_request(chatGPT: ChatGPT):
    pull_request = None
    for count in range(5):
        if pull_request:
            return pull_request
        try:
            logger.info(f"Generating for the {count}th time...")
            pr_text_response = chatGPT.chat(pull_request_prompt)
            pull_request = PullRequest.from_string(pr_text_response)
        except Exception:
            logger.warning("Failed to parse! Retrying...")
            chatGPT.undo()
            continue
    raise Exception("Could not generate PR text")


def create_branch(repo: Repository, pull_request: PullRequest):
    base_branch = repo.get_branch(repo.default_branch)
    try:
        repo.create_git_ref(
            f"refs/heads/{pull_request.branch_name}", base_branch.commit.sha
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e


def commit_files_to_github(
    file_change_requests: list[FileChangeRequest],
    repo: Repository,
    chatGPT: ChatGPT,
    branch_name: str,
):
    logger.debug(file_change_requests)
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
                    logger.warning("Failed to parse. Retrying...")
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
                    logger.warning("Failed to parse. Retrying...")
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
