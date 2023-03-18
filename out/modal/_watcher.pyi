from ._output import OutputManager as OutputManager
from _typeshed import Incomplete
from modal.mount import _Mount
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional, Set
from watchfiles import Change as Change, DefaultFilter

class StubFilesFilter(DefaultFilter):
    dir_filters: Incomplete
    def __init__(self, *, dir_filters: Dict[Path, Optional[Set[str]]]) -> None: ...
    def __call__(self, change: Change, path: str) -> bool: ...

async def watch(mounts: List[_Mount], output_mgr: OutputManager, timeout: Optional[float]) -> AsyncGenerator[None, None]: ...
