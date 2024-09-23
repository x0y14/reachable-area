from typing import Optional

from engine.yahoo_transit import *
from engine.train import *


if __name__ == "__main__":
    train_station_datas = load_station_data(
        "../../dataset/stations/N02-20_Station.geojson"
    )

    transit_type = TransitType.TRAIN

    honAtsugi_station: Optional[Station] = None
    shinjuku_station: Optional[Station] = None

    for train_station_data in train_station_datas:
        if train_station_data.name == "本厚木":
            honAtsugi_station = train_station_data
        elif train_station_data.name == "新宿":
            shinjuku_station = train_station_data

    routes = get_route_yahoo_transit(transit_type, honAtsugi_station, shinjuku_station)
    for route in routes:
        print(route)
        # {'time_required': 43, 'transfer': 0, 'fare': 513, 'distance': 45.4}
        # {'time_required': 48, 'transfer': 2, 'fare': 779, 'distance': 46.9}
        # {'time_required': 46, 'transfer': 2, 'fare': 837, 'distance': 46.3}
