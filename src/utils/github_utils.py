import re


def make_valid_string(string: str):
    pattern = r"[^\w./-]+"
    return re.sub(pattern, "_", string)


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
