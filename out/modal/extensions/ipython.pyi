from modal import Stub as Stub
from modal.config import config as config, logger as logger
from typing import Any

app_ctx: Any

def load_ipython_extension(ipython) -> None: ...
def unload_ipython_extension(ipython) -> None: ...
