import json
from geometry import *
from busstop import *


def convert_busstop_geojson_to_dataclass(geojson: dict) -> BusStop:
    # なぜか逆になってる
    coord = [geojson["geometry"]["coordinates"][1], geojson["geometry"]["coordinates"][0]]
    geo = Geometry(
        type=geojson["geometry"]["type"],
        coordinates=coord
    )
    routes = str(geojson["properties"]["P11_003_01"]).split(",")
    busstop = BusStop(
        name=geojson["properties"]["P11_001"],
        group=geojson["properties"]["P11_002"],
        routes=routes,
        geometry=geo
    )
    return busstop


def get_busstops_from_geojson(geojson: dict) -> list[BusStop]:
    busstops = []
    for feature in geojson["features"]:
        busstops.append(
            convert_busstop_geojson_to_dataclass(feature)
        )
    return busstops


def main():
    # [データ読み込み]
    # バス停
    kanagawa_bus_stops_geojson = None
    with open("dataset/busstpos/kanagawa/P11-22_14.geojson") as f:
        kanagawa_bus_stops_geojson = json.load(f)

    # [データの加工]
    # バス停
    kanagawa_bus_stops = get_busstops_from_geojson(kanagawa_bus_stops_geojson)

    for kanagawa_bus_stop in kanagawa_bus_stops:
        print(kanagawa_bus_stop)


if __name__ == "__main__":
    main()
