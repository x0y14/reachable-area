import json

from .bus_stop import *


def load_stop_data(path: str) -> list[BusStop]:
    stops = []

    j = None
    with open(path, "r") as f:
        j = json.load(f)
    if j is None:
        raise Exception(f"failed to read file: {path}")

    for feature in j["features"]:
        name = feature["properties"]["P11_001"]
        group = str(feature["properties"]["P11_002"]).split("・")
        lng, lat = feature["geometry"]["coordinates"]
        typ = feature["geometry"]["type"]

        geo = Geometry(Type=typ, Coordinates=[Coordinate(Lng=lng, Lat=lat)])
        routes = str(feature["properties"]["P11_003_01"]).split(",")

        stop = BusStop(name=name, group=group, routes=routes, geometry=geo)
        stops.append(stop)

    return stops
