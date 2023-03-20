from github.Repository import Repository
from loguru import logger

from src.common.models import (
    FileChangeRequest,
    PullRequest,
)
from src.common.sweep_bot import SweepBot


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
    sweep_bot: SweepBot,
    branch_name: str,
):
    logger.debug(file_change_requests)
    for file_change_request in file_change_requests:
        if file_change_request.change_type == "create":
            file_change = sweep_bot.create_file(file_change_request)
            # file_change = None
            # while not file_change:
            #     create_file_response = sweep_bot.chat(
            #         create_file_prompt.format(
            #             filename=file.filename,
            #             instructions=file.instructions,
            #         )
            #     )
            #     try:
            #         file_change = FileChange.from_string(create_file_response)
            #     except Exception:
            #         logger.warning("Failed to parse. Retrying...")
            #         sweep_bot.undo()
            #         continue
            # commit_message = f"sweep: {file_change.commit_message[:50]}"
            logger.debug(
                f"{file_change_request.filename}, {file_change.commit_message}, {file_change.code}, {branch_name}"
            )
            repo.create_file(
                file_change_request.filename,
                file_change.commit_message,
                file_change.code,
                branch=branch_name,
            )
        elif file_change_request.change_type == "modify":
            contents = repo.get_contents(file_change_request.filename, ref=branch_name)
            assert not isinstance(contents, list)
            file_change = sweep_bot.modify_file(
                file_change_request, contents.decoded_content.decode("utf-8")
            )
            # commit_message = f"sweep: {file_change.commit_message[:50]}"
            logger.debug(
                f"{file_change_request.filename}, {file_change.commit_message}, {file_change.code}, {branch_name}"
            )
            repo.update_file(
                file_change_request.filename,
                file_change.commit_message,
                file_change.code,
                contents.sha,
                branch=branch_name,
            )
        else:
            raise Exception("Invalid change type")
