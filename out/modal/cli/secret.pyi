from _typeshed import Incomplete
from modal.cli.utils import timestamp_to_local as timestamp_to_local
from modal.client import Client as Client
from typing import List

secret_cli: Incomplete

async def list() -> None: ...
def create(secret_name, keyvalues: List[str] = ...): ...
def get_text_from_editor(key) -> str: ...
