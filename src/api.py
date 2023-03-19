import modal  # type: ignore
from src.chains.on_ticket import on_ticket
from src.events import CommentCreatedEvent, IssueRequest

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
