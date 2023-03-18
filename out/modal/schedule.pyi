from _typeshed import Incomplete

class Schedule:
    proto_message: Incomplete
    def __init__(self, proto_message) -> None: ...

class Cron(Schedule):
    def __init__(self, cron_string: str) -> None: ...

class Period(Schedule):
    def __init__(self, years: int = ..., months: int = ..., weeks: int = ..., days: int = ..., hours: int = ..., minutes: int = ..., seconds: float = ...) -> None: ...
