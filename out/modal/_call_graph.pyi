from _typeshed import Incomplete
from enum import IntEnum
from modal_proto import api_pb2
from typing import List

class InputStatus(IntEnum):
    PENDING: int
    SUCCESS: Incomplete
    FAILURE: Incomplete
    TERMINATED: Incomplete
    TIMEOUT: Incomplete

class InputInfo:
    input_id: str
    task_id: str
    status: InputStatus
    function_name: str
    module_name: str
    children: List['InputInfo']
    def __init__(self, input_id, task_id, status, function_name, module_name, children) -> None: ...

def reconstruct_call_graph(ser_graph: api_pb2.FunctionGetCallGraphResponse) -> List[InputInfo]: ...
