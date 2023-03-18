import click
from .import_refs import import_function as import_function, import_stub as import_stub
from _typeshed import Incomplete
from modal._live_reload import run_serve_loop as run_serve_loop
from modal.exception import InvalidError as InvalidError
from modal.stub import LocalEntrypoint as LocalEntrypoint
from typing import Optional

run_cli: Incomplete
option_parsers: Incomplete

class NoParserAvailable(InvalidError): ...

class RunGroup(click.Group):
    def get_command(self, ctx, func_ref): ...

def run(ctx, detach) -> None: ...
def deploy(stub_ref: str = ..., name: str = ...): ...
def serve(stub_ref: str = ..., timeout: Optional[float] = ...): ...
def shell(func_ref: str = ..., cmd: str = ...): ...
