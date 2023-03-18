import modal
from src.chains.on_ticket import *

stub = modal.Stub("handle-ticket")
git_image = modal.Image.debian_slim().apt_install("git").pip_install("openai", "PyGithub")

@stub.webhook(method="POST", image=git_image, 
              secrets=[modal.Secret.from_name("bot-token"), modal.Secret.from_name("openai-secret")])
def handle_ticket(request: dict):
    # TODO: use pydantic
    if "issue" in request and request["action"] == "opened":
        title = request["issue"]["title"]
        body = request["issue"]["body"]
        if body is None:
            body = ""
        number = request["issue"]["number"]
        issue_url = request["issue"]["html_url"]
        username = request["issue"]["user"]["login"]
        repo_full_name = request["repository"]["full_name"]
        repo_description = request["repository"]["description"]
        if repo_description is None:
            repo_description = ""
        return on_ticket(title, body, number, issue_url, username, repo_full_name, repo_description)
    return {"success": True}
