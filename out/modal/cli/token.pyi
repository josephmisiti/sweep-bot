from _typeshed import Incomplete
from modal.client import Client as Client
from modal.config import config as config, user_config_path as user_config_path
from typing import Optional

token_cli: Incomplete
env_option: Incomplete

def set(token_id: Optional[str] = ..., token_secret: Optional[str] = ..., env: Optional[str] = ..., no_verify: bool = ...): ...
def new(env: Optional[str] = ..., no_verify: bool = ...): ...
