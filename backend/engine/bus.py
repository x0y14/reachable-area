import json

from .station import *


def load_stop_data(path: str) -> list[Station]:
    stops = []

    j = None
    with open(path, "r") as f:
        j = json.load(f)
    if j is None:
        raise Exception(f"failed to read file: {path}")

    for feature in j["features"]:
        name = feature["properties"]["P11_001"]
        groups = str(feature["properties"]["P11_002"]).split("・")
        lng, lat = feature["geometry"]["coordinates"]
        typ = feature["geometry"]["type"]

        geo = Geometry(Type=typ, Coordinates=[Coordinate(Lng=lng, Lat=lat)])
        routes = str(feature["properties"]["P11_003_01"]).split(",")

        stop = Station(
            transit_type=TransitType.BUS,
            name=name,
            management_groups=groups,
            line_routes=routes,
            geometry=geo,
            raw_feature=feature,
        )
        stops.append(stop)

    return stops
