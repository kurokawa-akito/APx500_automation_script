import typing
from System import Attribute

class ObsoleteInVersionAttribute(Attribute):
    def __init__(self, version: str) -> None: ...
    Version : str
    @property
    def TypeId(self) -> typing.Any: ...

