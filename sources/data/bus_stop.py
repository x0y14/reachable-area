import dataclasses

from sources.data.geo import *


@dataclasses.dataclass
class BusStop:
    name: str
    group: list[str]
    routes: list[str]
    geometry: Geometry

    def __str__(self):
        return f"{'・'.join(self.group)}-{self.name}"

    def __eq__(self, other):
        return str(self) == str(other)
