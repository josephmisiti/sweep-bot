from ._blob_utils import LARGE_FILE_LIMIT as LARGE_FILE_LIMIT, blob_iter as blob_iter, blob_upload_file as blob_upload_file
from ._resolver import Resolver as Resolver
from .object import Handle as Handle, Provider as Provider
from _typeshed import Incomplete
from modal_proto import api_pb2
from pathlib import Path, PurePosixPath
from typing import AsyncIterator, BinaryIO, List, Optional, Union

SHARED_VOLUME_PUT_FILE_CLIENT_TIMEOUT: Incomplete

class _SharedVolumeHandle(Handle):
    async def write_file(self, remote_path: str, fp: BinaryIO) -> int: ...
    async def read_file(self, path: str) -> AsyncIterator[bytes]: ...
    async def iterdir(self, path: str) -> AsyncIterator[api_pb2.SharedVolumeListFilesEntry]: ...
    async def add_local_file(self, local_path: Union[Path, str], remote_path: Optional[Union[str, PurePosixPath, None]] = ...): ...
    async def add_local_dir(self, local_path: Union[Path, str], remote_path: Optional[Union[str, PurePosixPath, None]] = ...): ...
    async def listdir(self, path: str) -> List[api_pb2.SharedVolumeListFilesEntry]: ...
    async def remove_file(self, path: str, recursive: bool = ...): ...

SharedVolumeHandle: Incomplete
AioSharedVolumeHandle: Incomplete

class _SharedVolume(Provider[_SharedVolumeHandle]):
    def __init__(self, cloud_provider: Optional[api_pb2.CloudProvider.V] = ...) -> None: ...

SharedVolume: Incomplete
AioSharedVolume: Incomplete
