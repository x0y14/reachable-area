import json
from lib.bus import *


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
