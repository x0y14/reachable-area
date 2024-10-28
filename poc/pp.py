from dotenv import load_dotenv

from engine import search_nearby_walking_distance_stations, get_stations_contain_area, get_same_line_or_route_stations, \
    get_route_yahoo_transit, get_same_line_or_route_stations_with_time, search_nearby_stations
from engine.mapbox import MapBoxApi, IsochroneProfile, concat_isochrones, isochrone_to_str
import os
from engine.bus import *
from engine.train import *
from collections import deque

from engine import get_reachable_stations


# データの読み込み
dataset: dict[TransitType, list[Station]] = {
    TransitType.BUS: load_stop_data("../dataset/busstops/kanagawa/P11-22_14.geojson"),
    TransitType.TRAIN: load_station_data("../dataset/stations/N02-20_Station.geojson"),
}
load_dotenv()
mapbox_api = MapBoxApi(os.getenv("MAPBOX_API_TOKEN"))


def get_reachable_stations2(
        api: MapBoxApi,
        dataset: dict[TransitType, list[Station]],
        start_point: Coordinate,
        time_limit: int,
        transit_types: list[TransitType]):

    queue = deque([(0, start_point)])
    checked: list[Station] = []
    reachable_stations:list[tuple[int, Station]] = []

    while len(queue) > 0:
        print("queue:", len(queue))
        q_travel_time, q_from = queue.popleft()
        # 時間制限を超える移動時間の駅は排除
        if not(q_travel_time < time_limit):
            continue
        # APIでエラーになるものを排除
        if not(1<=q_travel_time<=60):
            continue
        # 最寄りの駅取得
        for nearby in search_nearby_stations(api, dataset, q_from, time_limit-q_travel_time, transit_types):
            nearby_station_travel_time=nearby[0]
            nearby_station=nearby[1]
            # チェック済みなら飛ばす
            if nearby_station in checked:
                continue
            # 待機中なら飛ばす
            if nearby_station.geometry.calc_mean() in queue:
                continue
            queue.append([nearby_station_travel_time, ])



    return reachable_stations



if __name__=="__main__":
    # 厚木市役所を入力とする.
    input_coordinate = Coordinate(Lat=35.4429973, Lng=139.3611488)
    # 上記まで30分で行ける範囲を検索する
    input_time_limit = 30

    print("厚木市役所から")
    nearby_stations = get_reachable_stations2(
        api=mapbox_api,
        dataset=dataset,
        start_point=input_coordinate,
        time_limit=input_time_limit,
        transit_types=[TransitType.BUS]
    )

    for travel_time, nearby_station in nearby_stations:
        print(f"{travel_time}分: {nearby_station.name}")

