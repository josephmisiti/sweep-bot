import urllib.request
from pydantic import BaseModel

import modal

stub = modal.Stub("handle-ticket-webhook")

class Item(BaseModel):
    pr: str = "abc"

@stub.webhook(method="POST")
def handle_ticket(x: Item):
    print(x)
    return {"filename": "hello.py", "description": "Hello world!", "code": 'print("Hello world!")', 'pr': x.pr}