from loguru import logger


from src.common.models import (
    ChatGPT,
    FileChange,
    FileChangeRequest,
    FilesToChange,
    PullRequest,
    RegexMatchError,
)
from src.common.prompts import (
    files_to_change_prompt,
    pull_request_prompt,
    create_file_prompt,
    modify_file_prompt,
)


class SweepBot(ChatGPT):
    def get_files_to_change(self):
        file_change_requests: list[FileChangeRequest] = []
        for count in range(5):
            try:
                logger.info(f"Generating for the {count}th time...")
                files_to_change_response = self.chat(files_to_change_prompt)
                files_to_change = FilesToChange.from_string(files_to_change_response)
                files_to_create: list[str] = files_to_change.files_to_create.split("*")
                files_to_modify: list[str] = files_to_change.files_to_modify.split("*")
                logger.debug(files_to_change)
                for file_change_request, change_type in zip(
                    files_to_create + files_to_modify,
                    ["create"] * len(files_to_create)
                    + ["modify"] * len(files_to_modify),
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
                if file_change_requests:
                    return file_change_requests
            except RegexMatchError:
                logger.warning("Failed to parse! Retrying...")
                self.undo()
                continue
        raise Exception("Could not generate files to change")

    def generate_pull_request(self):
        pull_request = None
        for count in range(5):
            try:
                logger.info(f"Generating for the {count}th time...")
                pr_text_response = self.chat(pull_request_prompt)
                pull_request = PullRequest.from_string(pr_text_response)
                return pull_request
            except Exception:
                logger.warning("Failed to parse! Retrying...")
                self.undo()
                continue
        raise Exception("Could not generate PR text")

    def create_file(self, file_change_request: FileChangeRequest) -> FileChange:
        file_change: FileChange | None = None
        for count in range(5):
            create_file_response = self.chat(
                create_file_prompt.format(
                    filename=file_change_request.filename,
                    instructions=file_change_request.instructions,
                )
            )
            try:
                file_change = FileChange.from_string(create_file_response)
                file_change.commit_message = f"sweep: {file_change.commit_message[:50]}"
                return file_change
            except Exception:
                logger.warning(f"Failed to parse. Retrying for the {count}th time...")
                self.undo()
                continue
        raise Exception("Failed to parse response after 5 attempts.")

    def modify_file(
        self, file_change_request: FileChangeRequest, contents: str
    ) -> FileChange:
        file_change: FileChange | None = None
        for count in range(5):
            modify_file_response = self.chat(
                modify_file_prompt.format(
                    filename=file_change_request.filename,
                    instructions=file_change_request.instructions,
                    code=contents,
                )
            )
            try:
                file_change = FileChange.from_string(modify_file_response)
                file_change.commit_message = f"sweep: {file_change.commit_message[:50]}"
                return file_change
            except Exception:
                logger.warning(
                    f"Failed to parse. Retryinging for the {count}th time..."
                )
                self.undo()
                continue
        raise Exception("Failed to parse response after 5 attempts.")
