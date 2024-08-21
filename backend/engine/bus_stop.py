import dataclasses

from .geo import *


@dataclasses.dataclass
class BusStop:
    name: str
    management_groups: list[str]
    routes: list[str]
    geometry: Geometry
    raw_feature: dict

    def __str__(self):
        return f"{'・'.join(self.management_groups)}-{self.name}"

    def __eq__(self, other):
        return str(self) == str(other)

    def to_json(self) -> str:
        return json.dumps(
            {
                "name": self.name,
                "management_groups": self.management_groups,
                "routes": self.routes,
                "geometry": self.geometry.to_json(),
                "raw_feature": self.raw_feature,
            }
        )

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "management_groups": self.management_groups,
            "routes": self.routes,
            "geometry": self.geometry.as_dict(),
            "raw_feature": self.raw_feature,
        }
