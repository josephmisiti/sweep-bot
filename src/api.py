from loguru import logger
import modal  # type: ignore
from src.handlers.on_ticket import on_ticket
from src.handlers.on_comment import on_comment
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
handle_comment = stub.function(image=image, secrets=secrets)(on_comment)


@stub.webhook(method="POST", image=image, secrets=secrets)
def handle_ticket_webhook(request: IssueRequest):
    logger.info("handle_ticket_webhook called!")
    if (
        request.issue is not None
        and (
            request.action == "opened"
            or (request.action == "assigned" and request.assignee.login == "sweepaibot")
        )
        and request.issue.assignees
        and "sweepaibot" in [assignee.login for assignee in request.issue.assignees]
    ):
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
    print("action: ", comment.action)
    if comment.action != "created":
        return {"success": True}
    handle_comment.spawn(
        repo_full_name=comment.repository.full_name,
        repo_description=comment.repository.description,
        branch_name=comment.pull_request.head.ref,
        comment=comment.comment.body,
        path=comment.comment.path,
        pr_title=comment.pull_request.title,
        pr_body=comment.pull_request.body,
        pr_line_position=comment.comment.original_line,
    )
    return {"success": True}
