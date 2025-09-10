import typing

class DashStyle(typing.SupportsInt):
    @typing.overload
    def __init__(self, value : int) -> None: ...
    @typing.overload
    def __init__(self, value : int, force_if_true: bool) -> None: ...
    def __int__(self) -> int: ...
    
    # Values:
    Solid : DashStyle # 0
    Dash : DashStyle # 1
    Dot : DashStyle # 2
    DashDot : DashStyle # 3
    DashDotDot : DashStyle # 4
    Custom : DashStyle # 5

