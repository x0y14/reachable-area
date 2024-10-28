from collections import deque
from hmac import trans_5C
from tabnanny import check

from engine import get_same_line_or_route_stations, get_same_line_or_route_stations_with_time
from engine.mapbox import MapBoxApi, IsochroneProfile
from engine.train import *
import geopandas
from shapely.geometry import Point

import dataclasses
@dataclasses.dataclass
class StationWithIsochrone:
    station: Station
    isochrone: dict


def search_nearby_walking_distance_stations(
        api: MapBoxApi,
        dataset: dict[TransitType, list[Station]],
        coordinate: Coordinate,
        time_limits: list[int],
        transit_types: list[TransitType]
) -> dict[int, list[Station]]:
    nearby_stations: dict[int, list[Station]] = {tl: [] for tl in time_limits}
    walking_areas_with_time_limit: dict[int, geopandas.GeoDataFrame] = {}

    # MapboxApiを用いてisochroneを取得
    isochrones: dict = api.get_isochrone(
        prof=IsochroneProfile.Walking,
        coordinate=coordinate,
        contours_minutes=time_limits,
    )

    # Isochroneの加工
    for time_limit in time_limits:
        isochrone: dict = [isochrone for isochrone in isochrones["features"] if isochrone["properties"]["contour"] == time_limit][0]
        isochrone_gpd = geopandas.GeoDataFrame.from_features(
            {"features": [isochrone], "type": "FeatureCollection"}
        )
        walking_areas_with_time_limit[time_limit] = isochrone_gpd


    # チェック対象を確認
    candidates: list[Station] = []
    if TransitType.BUS in transit_types:
        candidates += dataset[TransitType.BUS]
    if TransitType.TRAIN in transit_types:
        candidates += dataset[TransitType.TRAIN]

    # チェック
    for candidate in candidates:
        candidate_coord = candidate.geometry.calc_mean()
        candidate_point = Point(candidate_coord.Lng, candidate_coord.Lat)
        for time_limit, walking_area in walking_areas_with_time_limit.items():
            is_include = bool(walking_area.contains(candidate_point)[0])
            if is_include:
                nearby_stations[time_limit].append(candidate)

    return nearby_stations


# search_nearby_walking_distance_stationsのisochroneを既に持ってる場合の版
def get_stations_contain_area(
        dataset: dict[TransitType, list[Station]],
        isochrone: dict,
        transit_types: list[TransitType]
) -> list[Station]:
    nearby_stations: list[Station] = []

    isochrone_gpd = geopandas.GeoDataFrame.from_features(isochrone)

    # チェック対象を確認
    candidates: list[Station] = []
    if TransitType.BUS in transit_types:
        candidates += dataset[TransitType.BUS]
    if TransitType.TRAIN in transit_types:
        candidates += dataset[TransitType.TRAIN]

    for candidate in candidates:
        candidate_coord = candidate.geometry.calc_mean()
        candidate_point = Point(candidate_coord.Lng, candidate_coord.Lat)
        is_include = bool(isochrone_gpd.contains(candidate_point)[0])
        if is_include:
            nearby_stations.append(candidate)

    return nearby_stations


def search_nearby_stations(api: MapBoxApi, dataset: dict[TransitType, list[Station]], start_point: Coordinate, time_limit: int, station_transit_types: list[TransitType]) ->list[tuple[int, Station]]:
    walking_distance_area = api.get_isochrone(
        prof=IsochroneProfile.Walking,
        coordinate=start_point,
        contours_minutes=[time_limit]
    )
    nearby_stations = get_stations_contain_area(
        dataset=dataset,
        isochrone=walking_distance_area,
        transit_types=station_transit_types,
    )

    nearby_stations_with_travel_time: list[tuple[int, Station]] = []
    for nearby_station in nearby_stations:
        travel_time_from_start_point = api.get_walking_travel_time(
            start_point,
            nearby_station.geometry.calc_mean()
        )
        nearby_stations_with_travel_time.append(
            (travel_time_from_start_point, nearby_station)
        )

    return nearby_stations_with_travel_time

def get_reachable_stations(
        api: MapBoxApi,
        dataset: dict[TransitType, list[Station]],
        start_point: Coordinate,
        time_limit: int,
        transit_types: list[TransitType]):

    checked_station: list[Station] = []
    queue_coordinate = deque([start_point])
    queue_travel_time = deque([0])

    reachable_stations = []

    while len(queue_coordinate) > 0:
        print("queue:",len(queue_coordinate))
        start_from = queue_coordinate.popleft()
        travel_time = queue_travel_time.popleft()

        # 移動に使える時間
        usable_time = time_limit-travel_time
        # 有効な残り時間がなければパス
        if not(1 <= usable_time <= 60) or  not(usable_time <= time_limit):
            continue

        # 入力の最寄りの駅を取得
        for nearby_station_travel_time, nearby_station in search_nearby_stations(api, dataset, start_from, usable_time, transit_types):
            # チェック済みか待機中なら飛ばす
            if (nearby_station in checked_station) or (nearby_station.geometry.calc_mean() in queue_coordinate):
                continue
            # チェック済み
            checked_station.append(nearby_station)
            # 総移動時間が期限以内であれば
            total_travel_time = travel_time+nearby_station_travel_time
            if total_travel_time <= time_limit:
                queue_coordinate.append(nearby_station.geometry.calc_mean())
                queue_travel_time.append(total_travel_time)
                reachable_stations.append((total_travel_time, nearby_station))
            else:
                continue

            # 交通機関に乗って辿り着ける場所探すよ
            transport_usable_time = time_limit-total_travel_time
            for transport_travel_time, transited_station in get_same_line_or_route_stations_with_time(nearby_station,dataset, transport_usable_time):
                if (transited_station in checked_station) or (transited_station.geometry.calc_mean() in queue_coordinate):
                    continue
                checked_station.append(nearby_station)
                total_transport_travel_time = total_travel_time+transport_travel_time
                if total_transport_travel_time <= time_limit:
                    queue_coordinate.append(transited_station.geometry.calc_mean())
                    queue_travel_time.append(total_transport_travel_time)
                    reachable_stations.append((total_transport_travel_time, transited_station))

    return reachable_stations
