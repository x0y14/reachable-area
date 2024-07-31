import json

import sources.data.geo as geo
from sources.data.train_station import TrainStation


def load_station_data(path: str) -> list[TrainStation]:
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
        ts_geometry = geo.load(feature["geometry"])

        ts = TrainStation(
            name=ts_name,
            management_group=ts_management_group,
            line=ts_line,
            train_code=ts_train_code,
            management_group_code=ts_management_group_code,
            geometry=ts_geometry,
            raw_feature=feature,
        )
        result.append(ts)

    return result


# if __name__ == "__main__":
#     r = load_station_data("../../dataset/stations/N02-20_Station.geojson")
#     print(r[3].geometry)
#     print(r[3].geometry.Coordinates)
