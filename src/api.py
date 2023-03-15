import modal

stub = modal.Stub("handle-ticket")

@stub.webhook(method="POST")
def handle_ticket(request: dict):
    # TODO: use pydantic
    if "issue" in request:
        title = request["issue"]["title"]
        body = request["issue"]["body"]
        if body is None:
            body = ""
        print(title, body)
    return {}
