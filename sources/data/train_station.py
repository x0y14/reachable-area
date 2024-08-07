import dataclasses

from sources.data.geo import *


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
