from ._function_utils import FunctionInfo as FunctionInfo
from ._ipython import is_notebook as is_notebook
from ._output import OutputManager as OutputManager
from ._pty import exec_cmd as exec_cmd
from .app import _App, is_local as is_local
from .client import _Client
from .config import logger as logger
from .exception import InvalidError as InvalidError, deprecation_warning as deprecation_warning
from .functions import _FunctionHandle
from .gpu import GPU_T as GPU_T
from .image import _Image
from .mount import _Mount
from .object import Provider as Provider
from .proxy import _Proxy
from .runner import deploy_stub as deploy_stub, run_stub as run_stub, serve_update as serve_update
from .schedule import Schedule as Schedule
from .secret import _Secret
from .shared_volume import _SharedVolume
from _typeshed import Incomplete
from multiprocessing.synchronize import Event
from typing import AsyncGenerator, Collection, Dict, List, Optional, Union

class LocalEntrypoint:
    raw_f: Incomplete
    def __init__(self, raw_f, stub) -> None: ...
    def __call__(self, *args, **kwargs): ...

class _Stub:
    def __init__(self, name: Optional[str] = ..., *, mounts: Collection[_Mount] = ..., secrets: Collection[_Secret] = ..., **blueprint) -> None: ...
    @property
    def name(self) -> str: ...
    @property
    def app(self) -> Optional[_App]: ...
    @property
    def description(self) -> str: ...
    def __getitem__(self, tag: str): ...
    def __setitem__(self, tag: str, obj: Provider): ...
    def __getattr__(self, tag: str) -> Provider: ...
    def __setattr__(self, tag: str, obj: Provider): ...
    def is_inside(self, image: Optional[_Image] = ...) -> bool: ...
    async def run(self, client: Optional[_Client] = ..., stdout: Incomplete | None = ..., show_progress: Optional[bool] = ..., detach: bool = ..., output_mgr: Optional[OutputManager] = ...) -> AsyncGenerator[_App, None]: ...
    async def serve(self, client: Optional[_Client] = ..., stdout: Incomplete | None = ..., show_progress: Optional[bool] = ..., timeout: float = ...) -> None: ...
    async def serve_update(self, existing_app_id: str, is_ready: Event) -> None: ...
    async def deploy(self, name: str = ..., namespace=..., client: Incomplete | None = ..., stdout: Incomplete | None = ..., show_progress: Incomplete | None = ..., object_entity: str = ...) -> _App: ...
    @property
    def registered_functions(self) -> Dict[str, _FunctionHandle]: ...
    @property
    def registered_entrypoints(self) -> Dict[str, LocalEntrypoint]: ...
    @property
    def registered_web_endpoints(self) -> List[str]: ...
    def local_entrypoint(self, raw_f: Incomplete | None = ..., name: Optional[str] = ...): ...
    def function(self, raw_f: Incomplete | None = ..., *, image: _Image = ..., schedule: Optional[Schedule] = ..., secret: Optional[_Secret] = ..., secrets: Collection[_Secret] = ..., gpu: GPU_T = ..., serialized: bool = ..., mounts: Collection[_Mount] = ..., shared_volumes: Dict[str, _SharedVolume] = ..., cpu: Optional[float] = ..., memory: Optional[int] = ..., proxy: Optional[_Proxy] = ..., retries: Optional[int] = ..., concurrency_limit: Optional[int] = ..., container_idle_timeout: Optional[int] = ..., timeout: Optional[int] = ..., interactive: bool = ..., keep_warm: Union[bool, int, None] = ..., name: Optional[str] = ..., is_generator: Optional[bool] = ..., cloud: Optional[str] = ...) -> _FunctionHandle: ...
    def webhook(self, raw_f, *, method: str = ..., label: str = ..., wait_for_response: bool = ..., image: _Image = ..., secret: Optional[_Secret] = ..., secrets: Collection[_Secret] = ..., gpu: GPU_T = ..., mounts: Collection[_Mount] = ..., shared_volumes: Dict[str, _SharedVolume] = ..., cpu: Optional[float] = ..., memory: Optional[int] = ..., proxy: Optional[_Proxy] = ..., retries: Optional[int] = ..., concurrency_limit: Optional[int] = ..., container_idle_timeout: Optional[int] = ..., timeout: Optional[int] = ..., keep_warm: Union[bool, int, None] = ..., cloud: Optional[str] = ...): ...
    def asgi(self, asgi_app, *, label: str = ..., wait_for_response: bool = ..., image: _Image = ..., secret: Optional[_Secret] = ..., secrets: Collection[_Secret] = ..., gpu: GPU_T = ..., mounts: Collection[_Mount] = ..., shared_volumes: Dict[str, _SharedVolume] = ..., cpu: Optional[float] = ..., memory: Optional[int] = ..., proxy: Optional[_Proxy] = ..., retries: Optional[int] = ..., concurrency_limit: Optional[int] = ..., container_idle_timeout: Optional[int] = ..., timeout: Optional[int] = ..., keep_warm: Union[bool, int, None] = ..., cloud: Optional[str] = ..., _webhook_type=...): ...
    def wsgi(self, wsgi_app, **kwargs): ...
    async def interactive_shell(self, cmd: Incomplete | None = ..., image: Incomplete | None = ..., **kwargs) -> None: ...

Stub: Incomplete
AioStub: Incomplete