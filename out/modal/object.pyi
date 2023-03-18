from ._object_meta import ObjectMeta as ObjectMeta
from ._resolver import Resolver as Resolver
from .client import _Client
from .exception import InvalidError as InvalidError, NotFoundError as NotFoundError, deprecation_warning as deprecation_warning
from _typeshed import Incomplete
from google.protobuf.message import Message as Message
from typing import Awaitable, Callable, Optional, TypeVar

H = TypeVar('H', bound='Handle')

class Handle(metaclass=ObjectMeta):
    def __init__(self) -> None: ...
    @classmethod
    async def from_id(cls, object_id: str, client: Optional[_Client] = ...) -> H: ...
    @property
    def object_id(self) -> str: ...
    @classmethod
    async def from_app(cls, app_name: str, tag: Optional[str] = ..., namespace=..., client: Optional[_Client] = ...) -> H: ...

lookup: Incomplete
aio_lookup: Incomplete
P = TypeVar('P', bound='Provider')

class Provider:
    def __init__(self, load: Callable[[Resolver, str], Awaitable[H]], rep: str) -> None: ...
    @classmethod
    def get_handle_cls(cls): ...
    @property
    def local_uuid(self): ...
    def persist(self, label: str, namespace=...): ...
    @classmethod
    def from_name(cls, app_name: str, tag: Optional[str] = ..., namespace=...) -> P: ...
    @classmethod
    async def lookup(cls, app_name: str, tag: Optional[str] = ..., namespace=..., client: Optional[_Client] = ...) -> H: ...
