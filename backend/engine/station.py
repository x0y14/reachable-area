import dataclasses
from .geo import *
from .transit_type import TransitType


@dataclasses.dataclass
class Station:
    transit_type: TransitType
    name: str
    management_groups: list[str]
    line_routes: list[str]
    geometry: Geometry
    raw_feature: dict

    def as_dict(self) -> dict:
        return {
            "transit_type": int(self.transit_type),
            "name": self.name,
            "management_groups": self.management_groups,
            "line_routes": self.line_routes,
            "geometry": self.geometry.as_dict(),
            "raw_feature": self.raw_feature,
        }

    def to_yahoo_transit(self) -> str:
        if self.transit_type == TransitType.BUS:
            return f"{self.name}/{self.management_groups[0]}".replace("（株）", "")
        elif self.transit_type == TransitType.TRAIN:
            return self.name

        return self.name
