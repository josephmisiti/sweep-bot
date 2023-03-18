from .exception import InvalidError as InvalidError, deprecation_warning as deprecation_warning
from _typeshed import Incomplete
from modal_proto import api_pb2

class _GPUConfig:
    type: api_pb2.GPUType.V
    count: int
    memory: int
    def __init__(self, type, count, memory) -> None: ...

class T4(_GPUConfig):
    def __init__(self) -> None: ...

class A100(_GPUConfig):
    def __init__(self, *, count: int = ..., memory: int = ...) -> None: ...

class A10G(_GPUConfig):
    def __init__(self, *, count: int = ...) -> None: ...

class Any(_GPUConfig):
    def __init__(self, *, count: int = ...) -> None: ...

STRING_TO_GPU_CONFIG: Incomplete
GPU_T: Incomplete

def parse_gpu_config(value: GPU_T, warn_on_true: bool = ...) -> api_pb2.GPUConfig: ...
def display_gpu_config(value: GPU_T) -> str: ...
