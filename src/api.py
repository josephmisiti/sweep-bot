import modal  # type: ignore
from pydantic import BaseModel
from src.chains.on_ticket import on_ticket

stub = modal.Stub("handle-ticket")
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .pip_install("openai", "PyGithub", "loguru")
)
secrets = [
    modal.Secret.from_name("bot-token"),
    modal.Secret.from_name("openai-secret"),
]


class IssueRequest(BaseModel):
    class Issue(BaseModel):
        class User(BaseModel):
            login: str

        title: str
        number: int
        html_url: str
        user: User
        body: str | None

    class Repository(BaseModel):
        full_name: str
        description: str | None

    action: str
    issue: Issue | None
    repository: Repository


handle_ticket = stub.function(image=image, secrets=secrets)(on_ticket)


@stub.webhook(method="POST", image=image, secrets=secrets)
def handle_ticket_webhook(request: IssueRequest):
    # TODO: use pydantic
    if request.issue is not None:
        if request.issue.body is None:
            request.issue.body = ""
        if request.repository.description is None:
            request.repository.description = ""
        handle_ticket.spawn(
            request.issue.title,
            request.issue.body,
            request.issue.number,
            request.issue.html_url,
            request.issue.user.login,
            request.repository.full_name,
            request.repository.description,
        )
    return {"success": True}


class CommentCreatedEvent(BaseModel):
    class Comment(BaseModel):
        body: str
        position: int
        path: str

    class PullRequest(BaseModel):
        class Head(BaseModel):
            ref: str

        body: str
        state: str  # "closed" or "open"
        head: Head

    class Repository(BaseModel):
        full_name: str
        description: str | None

    class Sender(BaseModel):
        pass

    action: str
    comment: Comment
    pull_request: PullRequest
    repository: Repository
    sender: Sender


@stub.webhook(method="POST", image=image, secrets=secrets)
def handle_comment_webhook(comment: CommentCreatedEvent):
    # TODO: use pydantic
    print("REQ: ", comment)
    print("Comment: ", comment.comment.body)
    print("Branch: ", comment.pull_request.head.ref)
    print("Path: ", comment.comment.path)
    print("Body: ", comment.comment.body)
    # handle_ticket.spawn(
    #     request.issue.title,
    #     request.issue.body,
    #     request.issue.number,
    #     request.issue.html_url,
    #     request.issue.user.login,
    #     request.repository.full_name,
    #     request.repository.description,
    # )
    return {"success": True}
