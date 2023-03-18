from _typeshed import Incomplete
from collections.abc import Generator
from typing import NamedTuple

pymc_stub: Incomplete
aio_pymc_stub: Incomplete

class ParallelSamplingError(Exception):
    def __init__(self, message, chain, warnings: Incomplete | None = ...) -> None: ...

class RemoteTraceback(Exception):
    tb: Incomplete
    def __init__(self, tb) -> None: ...

class ExceptionWithTraceback:
    exc: Incomplete
    tb: Incomplete
    def __init__(self, exc, tb) -> None: ...
    def __reduce__(self): ...

def rebuild_exc(exc, tb): ...
async def sample_process(draws: int, tune: int, step_method, chain: int, seed, start): ...

class Draw(NamedTuple):
    chain: Incomplete
    is_last: Incomplete
    draw_idx: Incomplete
    tuning: Incomplete
    stats: Incomplete
    point: Incomplete
    warnings: Incomplete

class _ModalSampler:
    def __init__(self, draws: int, tune: int, chains: int, cores: int, seeds: list, start_points, step_method, start_chain_num: int = ..., progressbar: bool = ..., mp_ctx: Incomplete | None = ..., pickle_backend: str = ...) -> None: ...
    async def __aiter__(self) -> Generator[Incomplete, None, None]: ...
    def __enter__(self): ...
    def __exit__(self, *args) -> None: ...

ModalSampler: Incomplete
