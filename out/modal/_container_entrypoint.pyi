from ._asgi import asgi_app_wrapper as asgi_app_wrapper, webhook_asgi_app as webhook_asgi_app, wsgi_app_wrapper as wsgi_app_wrapper
from ._blob_utils import MAX_OBJECT_SIZE_BYTES as MAX_OBJECT_SIZE_BYTES, blob_download as blob_download, blob_upload as blob_upload
from ._function_utils import load_function_from_module as load_function_from_module
from ._proxy_tunnel import proxy_tunnel as proxy_tunnel
from ._pty import run_in_pty as run_in_pty
from ._serialization import deserialize as deserialize, serialize as serialize
from ._traceback import extract_traceback as extract_traceback
from ._tracing import extract_tracing_context as extract_tracing_context, set_span_tag as set_span_tag, trace as trace, wrap as wrap
from .client import Client as Client, HEARTBEAT_INTERVAL as HEARTBEAT_INTERVAL, HEARTBEAT_TIMEOUT as HEARTBEAT_TIMEOUT
from .config import logger as logger
from .exception import InvalidError as InvalidError
from .functions import AioFunctionHandle as AioFunctionHandle, FunctionHandle as FunctionHandle
from _typeshed import Incomplete
from collections.abc import Generator
from modal_proto import api_pb2
from typing import Any, Callable, Optional

MAX_OUTPUT_BATCH_SIZE: int
RTT_S: float

class UserException(Exception): ...

class SequenceNumber:
    def __init__(self, initial_value: int) -> None: ...
    def increase(self) -> None: ...
    @property
    def value(self) -> int: ...

def get_is_async(function): ...
def run_with_signal_handler(coro): ...

class _FunctionIOManager:
    task_id: Incomplete
    function_id: Incomplete
    app_id: Incomplete
    function_def: Incomplete
    client: Incomplete
    calls_completed: int
    total_user_time: int
    current_input_id: Incomplete
    current_input_started_at: Incomplete
    def __init__(self, container_args, client) -> None: ...
    async def initialize_app(self) -> None: ...
    async def heartbeats(self) -> Generator[None, None, None]: ...
    async def get_serialized_function(self) -> tuple[Optional[Any], Callable]: ...
    def serialize(self, obj: Any) -> bytes: ...
    def deserialize(self, data: bytes) -> Any: ...
    async def populate_input_blobs(self, item): ...
    def get_average_call_time(self) -> float: ...
    def get_max_inputs_to_fetch(self): ...
    output_queue: Incomplete
    async def run_inputs_outputs(self) -> Generator[Incomplete, None, None]: ...
    def serialize_exception(self, exc: BaseException) -> Optional[bytes]: ...
    def serialize_traceback(self, exc: BaseException) -> tuple[Optional[bytes], Optional[bytes]]: ...
    async def handle_user_exception(self) -> Generator[None, None, None]: ...
    async def handle_input_exception(self, input_id, output_index: SequenceNumber): ...
    async def enqueue_output(self, input_id, output_index: int, data): ...
    async def enqueue_generator_value(self, input_id, output_index: int, data): ...
    async def enqueue_generator_eof(self, input_id, output_index: int): ...

FunctionIOManager: Incomplete
AioFunctionIOManager: Incomplete

def call_function_sync(function_io_manager, obj: Optional[Any], fun: Callable, is_generator: bool): ...
async def call_function_async(aio_function_io_manager, obj: Optional[Any], fun: Callable, is_generator: bool): ...
def import_function(function_def: api_pb2.Function, ser_cls, ser_fun) -> tuple[Any, Callable, bool]: ...
def main(container_args: api_pb2.ContainerArguments, client: Client): ...