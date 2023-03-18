from ._resolver import Resolver as Resolver
from .object import Handle as Handle, Provider as Provider
from _typeshed import Incomplete

class _SecretHandle(Handle): ...

class _Secret(Provider[_SecretHandle]):
    def __init__(self, env_dict=..., template_type: str = ...) -> None: ...

Secret: Incomplete
AioSecret: Incomplete
