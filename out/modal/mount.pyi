import abc
import typing
from ._blob_utils import FileUploadSpec as FileUploadSpec, blob_upload_file as blob_upload_file, get_file_upload_spec as get_file_upload_spec
from ._resolver import Resolver as Resolver
from .config import config as config, logger as logger
from .exception import InvalidError as InvalidError, NotFoundError as NotFoundError, deprecation_warning as deprecation_warning
from .object import Handle as Handle, Provider as Provider
from _typeshed import Incomplete
from collections.abc import Generator
from pathlib import Path, PurePosixPath
from typing import Callable, List, Optional, Tuple, Union

MOUNT_PUT_FILE_CLIENT_TIMEOUT: Incomplete

def client_mount_name(): ...

class _MountEntry(metaclass=abc.ABCMeta):
    remote_path: PurePosixPath
    def description(self) -> str: ...
    def get_files_to_upload(self) -> typing.Iterator[Tuple[Path, str]]: ...
    def watch_entry(self) -> Tuple[Path, Path]: ...

class _MountFile(_MountEntry):
    local_file: Path
    remote_path: PurePosixPath
    def description(self) -> str: ...
    def get_files_to_upload(self) -> Generator[Incomplete, None, None]: ...
    def watch_entry(self): ...
    def __init__(self, local_file, remote_path) -> None: ...

class _MountDir(_MountEntry):
    local_dir: Path
    remote_path: PurePosixPath
    condition: Callable[[str], bool]
    recursive: bool
    def description(self): ...
    def get_files_to_upload(self) -> Generator[Incomplete, None, None]: ...
    def watch_entry(self): ...
    def __init__(self, local_dir, remote_path, condition, recursive) -> None: ...

class _MountHandle(Handle): ...

class _Mount(Provider[_MountHandle]):
    def __init__(self, remote_dir: Union[str, PurePosixPath] = ..., *, local_dir: Optional[Union[str, Path]] = ..., local_file: Optional[Union[str, Path]] = ..., condition: Callable[[str], bool] = ..., recursive: bool = ..., _entries: Optional[List[_MountEntry]] = ...) -> None: ...
    def extend(self, *entries) -> _Mount: ...
    def is_local(self) -> bool: ...
    def add_local_dir(self, local_path: Union[str, Path], *, remote_path: Union[str, PurePosixPath, None] = ..., condition: Callable[[str], bool] = ..., recursive: bool = ...) -> _Mount: ...
    @staticmethod
    def from_local_dir(local_path: Union[str, Path], *, remote_path: Union[str, PurePosixPath, None] = ..., condition: Callable[[str], bool] = ..., recursive: bool = ...): ...
    def add_local_file(self, local_path: Union[str, Path], remote_path: Union[str, PurePosixPath, None] = ...) -> _Mount: ...
    @staticmethod
    def from_local_file(local_path: Union[str, Path], remote_path: Union[str, PurePosixPath, None] = ...) -> _Mount: ...

Mount: Incomplete
AioMount: Incomplete
aio_create_client_mount: Incomplete
create_package_mounts: Incomplete
aio_create_package_mounts: Incomplete
