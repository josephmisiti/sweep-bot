import typer
from .app import app_cli as app_cli
from .config import config_cli as config_cli
from .env import env_cli as env_cli
from .secret import secret_cli as secret_cli
from .token import token_cli as token_cli
from .volume import volume_cli as volume_cli
from _typeshed import Incomplete
from modal.cli import run as run

def version_callback(value: bool): ...

entrypoint_cli_typer: Incomplete

def modal(ctx: typer.Context, version: bool = ...): ...

entrypoint_cli: Incomplete
