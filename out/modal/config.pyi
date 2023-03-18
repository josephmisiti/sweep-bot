import typing
from ._traceback import setup_rich_traceback as setup_rich_traceback
from _typeshed import Incomplete

user_config_path: str

def config_envs(): ...
def config_set_active_env(env: str): ...

class _Setting(typing.NamedTuple):
    default: typing.Any
    transform: typing.Callable[[str], typing.Any]

class Config:
    def __init__(self) -> None: ...
    def get(self, key, env: Incomplete | None = ...): ...
    def __getitem__(self, key): ...

config: Incomplete
logger: Incomplete
log_level_numeric: Incomplete
