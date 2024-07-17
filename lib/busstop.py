import dataclasses

from lib.geometry import Geometry


@dataclasses.dataclass
class BusStop:
    name: str
    group: str
    routes: list[str]
    geometry: Geometry


# Sample
# BusStop(
#   name='峰岡上',
#   group='相鉄バス（株）',
#   routes=['浜5'],
#   geometry=Geometry(
#       type='Point',
#       coordinates=[139.5967436356555, 35.46710563861377])
# )
