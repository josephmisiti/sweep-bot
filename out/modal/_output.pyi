import io
from ._ipython import is_notebook as is_notebook
from .client import _Client
from .config import logger as logger
from _typeshed import Incomplete
from collections.abc import Generator
from modal_proto import api_pb2
from rich.console import RenderableType as RenderableType
from rich.live import Live
from rich.progress import Progress, ProgressColumn, TaskID as TaskID
from rich.spinner import Spinner
from rich.text import Text
from typing import Callable, Optional

default_spinner: str

class FunctionQueuingColumn(ProgressColumn):
    lag: int
    def __init__(self) -> None: ...
    def render(self, task) -> Text: ...

def step_progress(text: str = ...) -> Spinner: ...
def step_progress_update(spinner: Spinner, message: str): ...
def step_completed(message: str, is_substep: bool = ...) -> RenderableType: ...

class LineBufferedOutput(io.StringIO):
    LINE_REGEX: Incomplete
    def __init__(self, callback: Callable[[str], None]) -> None: ...
    def write(self, data: str): ...
    def flush(self) -> None: ...
    def finalize(self) -> None: ...

class OutputManager:
    stdout: Incomplete
    def __init__(self, stdout: io.TextIOWrapper, show_progress: Optional[bool], status_spinner_text: str = ...) -> None: ...
    def print_if_visible(self, renderable) -> None: ...
    def ctx_if_visible(self, context_mgr): ...
    def make_live(self, renderable: RenderableType) -> Live: ...
    @property
    def function_progress(self) -> Progress: ...
    @property
    def snapshot_progress(self) -> Progress: ...
    @property
    def function_queueing_progress(self) -> Progress: ...
    def function_progress_callback(self, tag: str) -> Callable[[int, int], None]: ...
    def update_task_state(self, task_id: str, state: int): ...
    def update_snapshot_progress(self, image_id: str, task_progress: api_pb2.TaskProgress) -> None: ...
    def update_queueing_progress(self, *, function_id: str, completed: int, total: Optional[int], description: Optional[str]) -> None: ...
    async def put_log_content(self, log: api_pb2.TaskLogs): ...
    def flush_lines(self) -> None: ...
    def show_status_spinner(self) -> Generator[None, None, None]: ...

async def get_app_logs_loop(app_id: str, client: _Client, output_mgr: OutputManager): ...