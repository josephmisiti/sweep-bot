from ._output import OutputManager as OutputManager, get_app_logs_loop as get_app_logs_loop, step_completed as step_completed
from .app import _App, is_local as is_local
from .client import HEARTBEAT_INTERVAL as HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT as HEARTBEAT_TIMEOUT, _Client
from .config import config as config
from .exception import InvalidError as InvalidError
from _typeshed import Incomplete
from multiprocessing.synchronize import Event
from typing import AsyncGenerator, Optional

async def run_stub(stub, client: Optional[_Client] = ..., stdout: Incomplete | None = ..., show_progress: Optional[bool] = ..., detach: bool = ..., output_mgr: Optional[OutputManager] = ...) -> AsyncGenerator[_App, None]: ...
async def serve_update(stub, existing_app_id: str, is_ready: Event) -> None: ...
async def deploy_stub(stub, name: str = ..., namespace=..., client: Incomplete | None = ..., stdout: Incomplete | None = ..., show_progress: Incomplete | None = ..., object_entity: str = ...) -> _App: ...
