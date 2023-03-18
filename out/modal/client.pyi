from ._tracing import inject_tracing_context as inject_tracing_context
from .config import config as config, logger as logger
from .exception import AuthError as AuthError, ConnectionError as ConnectionError, DeprecationError as DeprecationError, VersionError as VersionError
from _typeshed import Incomplete
from typing import Callable

HEARTBEAT_INTERVAL: Incomplete
HEARTBEAT_TIMEOUT: float
CLIENT_CREATE_ATTEMPT_TIMEOUT: float
CLIENT_CREATE_TOTAL_TIMEOUT: float

class _Client:
    server_url: Incomplete
    client_type: Incomplete
    credentials: Incomplete
    version: Incomplete
    no_verify: Incomplete
    def __init__(self, server_url, client_type, credentials, version=..., *, no_verify: bool = ...) -> None: ...
    @property
    def stub(self): ...
    def set_pre_stop(self, pre_stop: Callable[[], None]): ...
    async def __aenter__(self): ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
    @classmethod
    async def verify(cls, server_url, credentials) -> None: ...
    @classmethod
    async def unauthenticated_client(cls, env: str, server_url: str): ...
    async def start_token_flow(self) -> tuple[str, str]: ...
    async def finish_token_flow(self, token_flow_id) -> tuple[str, str]: ...
    @classmethod
    async def from_env(cls, _override_config: Incomplete | None = ...) -> _Client: ...
    @classmethod
    def set_env_client(cls, client) -> None: ...

Client: Incomplete
AioClient: Incomplete