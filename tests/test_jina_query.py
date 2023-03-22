from src.utils.github_utils import (
    get_relevant_directories,
    get_relevant_directories_remote,
    download_repository
)

from src.utils.jina_utils import JinaClient


def test_query_all():
    relevant_directories, relevant_files = get_relevant_directories(
        "How do I add exponential backoff to OpenAI calls?"
    )
    print(relevant_directories)
    print(relevant_files)


def test_query_jina():
    relevant_directories, relevant_files = get_relevant_directories_remote(
        "How do I add exponential backoff to OpenAI calls?",
        num_files=10,
    )
    print(relevant_directories)
    print(relevant_files)


if __name__ == '__main__':
    client = JinaClient(host='http://0.0.0.0:64908')
    docs = download_repository("sweepai/sweep", exclude_dirs=["tests", ".github"], include_exts=[".py"])
    client.index(docs)
    result = client.search("sweep")
    matches = result[0]["matches"]
    print(f'Matched Documents: {len(matches)}')
    for match in matches:
        print(f'File: {match["tags"]["file_path"]}: {match["scores"]}')
