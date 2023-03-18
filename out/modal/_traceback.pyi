from rich.console import RenderResult as RenderResult
from rich.traceback import Stack as Stack
from typing import Any, Dict, Tuple

TBDictType = Dict[str, Any]
LineCacheType = Dict[Tuple[str, str], str]

def extract_traceback(exc: BaseException, task_id: str) -> Tuple[TBDictType, LineCacheType]: ...
def append_modal_tb(exc: BaseException, tb_dict: TBDictType, line_cache: LineCacheType) -> None: ...
def setup_rich_traceback() -> None: ...
