from .exception import InvalidError as InvalidError
from _typeshed import Incomplete
from enum import Enum
from modal_proto import api_pb2

class CloudProvider(Enum):
    AWS: Incomplete
    GCP: Incomplete
    AUTO: Incomplete

def parse_cloud_provider(value: str) -> api_pb2.CloudProvider.V: ...
def display_location(cloud_provider: api_pb2.CloudProvider.V) -> str: ...
