from github import Repository

from loguru import logger
from src.chains.on_ticket_models import (
    ChatGPT,
    FileChange,
    FileChangeRequest,
    FilesToChange,
)
from src.chains.on_ticket_prompts import (
    files_to_change_prompt,
    create_file_prompt,
    modify_file_prompt,
)


def get_files_from_chatgpt(chatGPT: ChatGPT):
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
    return file_change_requests


def commit_files_to_github(
    file_change_requests: list[FileChangeRequest],
    repo: Repository,
    chatGPT: ChatGPT,
    branch_name: str,
):
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
