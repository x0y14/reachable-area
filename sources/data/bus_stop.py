import dataclasses

from sources.data.geo import *


@dataclasses.dataclass
class BusStop:
    name: str
    group: str
    routes: list[str]
    geometry: Geometry
