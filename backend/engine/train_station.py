import dataclasses

from .geo import *


@dataclasses.dataclass
class TrainStation:
    name: str
    management_group: str
    line: str
    train_code: int  # 鉄道区分コード: N02_001
    management_group_code: int  # 事業者種別コード
    geometry: Geometry
    raw_feature: dict

    def __str__(self):
        return f"{self.management_group}-{self.line}-{self.name}"

    def __eq__(self, other):
        return str(self) == str(other)

    def to_json(self) -> str:
        return json.dumps(
            {
                "name": self.name,
                "management_group": self.management_group,
                "line": self.line,
                "train_code": self.train_code,
                "management_group_code": self.management_group_code,
                "geometry": self.geometry.to_json(),
                "raw_feature": self.raw_feature,
            }
        )

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "management_group": self.management_group,
            "line": self.line,
            "train_code": self.train_code,
            "management_group_code": self.management_group_code,
            "geometry": self.geometry.as_dict(),
            "raw_feature": self.raw_feature,
        }
