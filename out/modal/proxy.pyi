from .object import Handle as Handle, Provider as Provider
from _typeshed import Incomplete

class _ProxyHandle(Handle): ...
class _Proxy(Provider[_ProxyHandle]): ...

ProxyHandle: Incomplete
AioProxyHandle: Incomplete
Proxy: Incomplete
AioProxy: Incomplete
