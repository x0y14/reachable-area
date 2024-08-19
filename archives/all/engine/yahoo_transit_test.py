from yahoo_transit import *
from train import *


if __name__ == "__main__":
    train_station_datas = load_station_data(
        "../dataset/stations/N02-20_Station.geojson"
    )

    transit_type = TransitType.TRAIN

    honAtsugi_station: TrainStation = None
    shinjuku_station: TrainStation = None

    for train_station_data in train_station_datas:
        if train_station_data.name == "本厚木":
            honAtsugi_station = train_station_data
        elif train_station_data.name == "新宿":
            shinjuku_station = train_station_data

    from_station_name = generate_train_station_name(honAtsugi_station)
    to_station_name = generate_train_station_name(shinjuku_station)

    routes = get_route_yahoo_transit(transit_type, from_station_name, to_station_name)
    for route in routes:
        print(route)
