import json

from . import Station, TransitType
from .geo import *


def load_station_data(path: str) -> list[Station]:
    data: dict = {}
    with open(path, "r") as f:
        data = json.load(f)

    result = []

    for feature in data["features"]:
        props = feature["properties"]

        ts_name = props["N02_005"]
        ts_management_group = props["N02_004"]
        ts_line = props["N02_003"]
        ts_train_code = int(props["N02_001"])
        ts_management_group_code = int(props["N02_002"])
        ts_geometry = load(feature["geometry"])

        ts = Station(
            transit_type=TransitType.TRAIN,
            name=ts_name,
            management_groups=[ts_management_group],
            line_routes=[ts_line],
            # train_code=ts_train_code,
            # management_group_code=ts_management_group_code,
            geometry=ts_geometry,
            raw_feature=feature,
        )
        result.append(ts)

    return result
