import os
import requests  # type: ignore

import modal  # type: ignore


stub = modal.Stub("tests")
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install("openai", "PyGithub", "loguru")
)
secrets = [
    modal.Secret.from_name("bot-token"),
    modal.Secret.from_name("openai-secret"),
]


@stub.function(image=image, secrets=secrets)
def test_new_ticket():
    owner = "sweepai"
    repo = "sweep"
    hook_id = "405087685"
    delivery_id = "d11c3e50-c52e-11ed-83fb-c7d7fddc3988"
    access_token = os.environ["GITHUB_TOKEN"]
    headers = {"Authorization": f"token {access_token}"}
    requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/hooks/{hook_id}/deliveries/{delivery_id}/attempts",
        headers=headers,
    )
