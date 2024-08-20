import csv

from backend.engine.bus import load_stop_data
from backend.engine.train import load_station_data
from backend.engine.transit_type import TransitType


def main():
    train_stations = load_station_data("../dataset/stations/N02-20_Station.geojson")
    bus_stops = load_stop_data("../dataset/busstpos/kanagawa/P11-22_14.geojson")

    with open("../dataset/summaries/points.csv", "w") as f:
        writer = csv.writer(f)
        # 電車の駅
        for station in train_stations:
            writer.writerow(
                [
                    int(TransitType.TRAIN),
                    station.management_group,
                    station.line,
                    station.name,
                ]
            )
        # バス停
        for stop in bus_stops:
            writer.writerow([int(TransitType.BUS), "・".join(stop.group), stop.name])


if __name__ == "__main__":
    main()
