from .config import logger as logger
from _typeshed import Incomplete
from typing import Any, Dict

class ObjectMeta(type):
    prefix_to_type: Dict[str, Any]
    def __new__(metacls, name, bases, dct, type_prefix: Incomplete | None = ...): ...
