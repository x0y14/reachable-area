import dataclasses

from sources.data.geo import *


@dataclasses.dataclass
class BusStop:
    name: str
    group: list[str]
    routes: list[str]
    geometry: Geometry
