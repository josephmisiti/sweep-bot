import os
import time
import re
from github import Github

from jwt import encode
import requests  # type: ignore
from src.utils.jina_utils import JinaClient
from docarray import Document, DocumentArray

JINA_ENDPOINT = "https://apt-mole-24b968d6c0.wolf.jina.ai  "


def make_valid_string(string: str):
    pattern = r"[^\w./-]+"
    return re.sub(pattern, "_", string)


def get_jwt():
    signing_key = os.environ["GITHUB_APP_PEM"]
    app_id = "307814"
    payload = {"iat": int(time.time()), "exp": int(time.time()) + 600, "iss": app_id}

    return encode(payload, signing_key, algorithm="RS256")


def get_token(installation_id: int):
    jwt = get_jwt()
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + jwt,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.post(
        f"https://api.github.com/app/installations/{installation_id}/access_tokens",
        headers=headers,
    )
    return response.json()["token"]


def get_github_client(installation_id: int):
    token = get_token(installation_id)
    return Github(token)


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

                    if file.name.endswith(".py"):
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


def get_relevant_directories_remote(query: str, num_files: int = 5) -> tuple[str, str]:
    # Initialize the relevant directories string
    relevant_directories = ""
    relevant_files = '"""'
    client = JinaClient(JINA_ENDPOINT)
    # filter_tags = {'repository': {'$eq': "sweepai/forked_langchain"}}
    result = client.search(query)
    relevant_dirs_set = set()
    matches = result[0]["matches"][:num_files]
    for match in matches:
        file_contents = match["text"]
        relevant_files += f'"""\n{file_contents}\n"""'
        file_path = match["tags"]["file_path"]
        if file_path not in relevant_dirs_set:
            relevant_dirs_set.add(file_path)
            relevant_directories += file_path.replace("src/", "") + "\n"

    # Print the relevant directories and files strings
    print(relevant_directories)
    print(relevant_files)
    return relevant_directories, relevant_files


def download_repository(repo_name: str, branch_name: str = None, include_dirs: list[str] = [], exclude_dirs: list[str] = [], include_exts: list[str] = [], exclude_exts: list[str] = []):
    # create a Github object using the access token
    g = Github(os.environ.get("GITHUB_TOKEN"))

    # get the repository object
    repo = g.get_repo(repo_name)

    # get the contents of the root directory of the repository
    if branch_name is None:
        contents = repo.get_contents("")
    else:
        contents = repo.get_contents("", ref=branch_name)

    # create an empty DocumentArray to hold the downloaded files
    docs = DocumentArray()

    # recursively download all files and directories
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            if file_content.name in include_dirs:
                contents.extend(repo.get_contents(file_content.path))
            elif file_content.name not in exclude_dirs:
                contents.extend(repo.get_contents(file_content.path))
        else:
            if any(file_content.name.endswith(ext) for ext in include_exts) and file_content.name != "__init__.py":
                if not any(file_content.name.endswith(ext) for ext in exclude_exts):
                    try:
                        text = file_content.decoded_content.decode("utf-8")
                        print("Decoded: " + file_content.path)
                    except Exception:
                        print("Failed Decoding: " + file_content.path)
                        continue
                    doc = Document(content=text, tags={'file_path': file_content.path, "repository": repo_name})
                    docs.append(doc)
    return docs


def index_full_repository(repo_name: str, branch_name: str = None, include_dirs: list[str] = [], exclude_dirs: list[str] = [], include_exts: list[str] = [], exclude_exts: list[str] = []):
    docs = download_repository(repo_name, branch_name, include_dirs, exclude_dirs, include_exts, exclude_exts)
    client = JinaClient(JINA_ENDPOINT)
    indexed = client.index(docs)
    return len(indexed)
