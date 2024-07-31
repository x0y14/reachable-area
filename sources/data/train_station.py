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
