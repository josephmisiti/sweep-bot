from github import UnknownObjectException, Repository

from src.chains.on_ticket_models import ChatGPT, FileChange


def get_files_from_chatgpt(pr_code_prompt: str, chatGPT: ChatGPT):
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
    return parsed_files


def commit_files_to_github(
    parsed_files: list[FileChange], repo: Repository, branch_name: str
):
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
