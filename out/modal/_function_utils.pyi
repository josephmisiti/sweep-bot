import typing
from ._serialization import serialize as serialize
from .config import config as config, logger as logger
from .exception import InvalidError as InvalidError
from .mount import _Mount
from _typeshed import Incomplete
from enum import Enum
from typing import Dict, Optional

ROOT_DIR: Incomplete
SYS_PREFIXES: Incomplete

class FunctionInfoType(Enum):
    PACKAGE: str
    FILE: str
    SERIALIZED: str
    NOTEBOOK: str

class LocalFunctionError(InvalidError): ...

def package_mount_condition(filename): ...
def filter_safe_mounts(mounts: typing.Dict[str, _Mount]): ...
def is_global_function(function_qual_name): ...

class FunctionInfo:
    raw_f: Incomplete
    function_name: Incomplete
    signature: Incomplete
    base_dir: Incomplete
    module_name: Incomplete
    remote_dir: Incomplete
    definition_type: Incomplete
    type: Incomplete
    serialized_function: Incomplete
    file: Incomplete
    def __init__(self, f, serialized: bool = ..., name_override: Optional[str] = ...) -> None: ...
    def get_mounts(self) -> Dict[str, _Mount]: ...
    def get_tag(self): ...
    def is_nullary(self): ...

def load_function_from_module(module, qual_name): ...
