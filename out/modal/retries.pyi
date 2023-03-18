from .exception import InvalidError as InvalidError
from _typeshed import Incomplete

class Retries:
    max_retries: Incomplete
    backoff_coefficient: Incomplete
    initial_delay: Incomplete
    max_delay: Incomplete
    def __init__(self, *, max_retries: int, backoff_coefficient: float = ..., initial_delay: float = ..., max_delay: float = ...) -> None: ...
