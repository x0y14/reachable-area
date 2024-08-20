from train import *


if __name__ == "__main__":
    r = load_station_data("../../dataset/stations/N02-20_Station.geojson")
    print(r[3].geometry)
    print(r[3].geometry.Coordinates)
