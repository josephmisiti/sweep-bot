import modal
from src.chains.on_ticket import *

stub = modal.Stub("handle-ticket")
git_image = modal.Image.debian_slim().apt_install("git").pip_install("GitPython", 'openai')

@stub.webhook(method="POST", image=git_image, 
              secrets=[modal.Secret.from_name("bot-token"), modal.Secret.from_name("openai-secret")])
def handle_ticket(request: dict):
    # TODO: use pydantic
    if "issue" in request and request["action"] == "opened":
        title = request["issue"]["title"]
        body = request["issue"]["body"]
        if body is None:
            body = ""
        return on_ticket(title, body, "")
    return {}
