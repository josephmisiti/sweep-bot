from ._resolver import Resolver as Resolver
from ._serialization import deserialize as deserialize, serialize as serialize
from .object import Handle as Handle, Provider as Provider
from _typeshed import Incomplete
from typing import Any, List, Optional

class _QueueHandle(Handle):
    async def get(self, block: bool = ..., timeout: Optional[float] = ...) -> Optional[Any]: ...
    async def get_many(self, n_values: int, block: bool = ..., timeout: Optional[float] = ...) -> List[Any]: ...
    async def put(self, v: Any) -> None: ...
    async def put_many(self, vs: List[Any]) -> None: ...

QueueHandle: Incomplete
AioQueueHandle: Incomplete

class _Queue(Provider[_QueueHandle]):
    def __init__(self) -> None: ...

Queue: Incomplete
AioQueue: Incomplete
