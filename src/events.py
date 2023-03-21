from pydantic import BaseModel


class CommentCreatedEvent(BaseModel):
    class Comment(BaseModel):
        body: str
        original_line: int
        path: str

    class PullRequest(BaseModel):
        class Head(BaseModel):
            ref: str

        body: str
        state: str  # "closed" or "open"
        head: Head
        title: str

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


class IssueRequest(BaseModel):
    class Issue(BaseModel):
        class User(BaseModel):
            login: str

        class Assignee(BaseModel):
            login: str

        title: str
        number: int
        html_url: str
        user: User
        body: str | None
        assignees: list[Assignee]

    class Repository(BaseModel):
        full_name: str
        description: str | None

    action: str
    issue: Issue | None
    repository: Repository
    assignee: Issue.Assignee
