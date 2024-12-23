from collections import deque
from hmac import trans_5C
from tabnanny import check
from typing import Optional

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

def _get_same_name_nearby_station(l: list[Station], t: Station) -> Optional[Station]:
    for candidate in l:
        if t.name == candidate.name and t.transit_type == candidate.transit_type and calc_distance_m(t.geometry.calc_mean(), candidate.geometry.calc_mean()) <= 1000:
            return candidate
    return None


def get_stations_contain_area_merge_same_name(
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
        # エリア内の駅を見つけた
        if is_include:
            # 重複を探す
            duplicate = _get_same_name_nearby_station(nearby_stations, candidate)
            if duplicate is None: # 重複はなかった
                nearby_stations.append(candidate)
            else: # 重複はあった
                if candidate.management_groups == duplicate.management_groups: # 管理会社が同じ
                    # スルーしちゃう
                    continue
                else:
                    if not set(candidate.management_groups).issubset(set(duplicate.management_groups)):
                        # すでにあったものを一旦消す.
                        nearby_stations.remove(duplicate)
                        # 共同管理する駅として登録しちゃう
                        candidate.management_groups = list(set([*candidate.management_groups, *duplicate.management_groups]))
                        candidate.line_routes = [*candidate.line_routes, *duplicate.management_groups]
                        candidate.geometry.Coordinates = [*candidate.geometry.Coordinates, *duplicate.geometry.Coordinates]
                        nearby_stations.append(candidate)

    return nearby_stations


def search_walking_area_stations(api: MapBoxApi, dataset: dict[TransitType, list[Station]], start_point: Coordinate, time_limit: int, station_transit_types: list[TransitType]) ->list[tuple[int, Station]]:
    walking_distance_area = api.get_isochrone(
        prof=IsochroneProfile.Walking,
        coordinate=start_point,
        contours_minutes=[time_limit]
    )
    nearby_stations = get_stations_contain_area_merge_same_name(
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
        if time_limit > travel_time_from_start_point:
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
        for nearby_station_travel_time, nearby_station in search_walking_area_stations(api, dataset, start_from, usable_time, transit_types):
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

@dataclasses.dataclass
class StationWithTravelTime:
    station: Station
    travel_time: int

def get_reachable_stations2(
        api: MapBoxApi,
        dataset: dict[TransitType, list[Station]],
        origin: Coordinate,
        time_limit: int,
        transit_types: list[TransitType]) -> list[StationWithTravelTime]:
    # 駒込->巣鴨，新宿->巣鴨，のように巣鴨が2階キューに入ってしまうことがある．
    # これを実行時にチェックするためのリスト
    checked_stations: list[Station] = []
    checked_coordinates: list[Coordinate] = []
    # 探索のための座標のキュー
    queue = deque([(origin, 0)]) # (座標, 行くのにかかる時間)
    # 結果
    reachable_stations: list[StationWithTravelTime] =[]

    while len(queue) > 0: # キューの中身がある場合
        # キューから探索スタート地点とそこまでの移動時間を取得
        q = queue.popleft()
        start_point = q[0]
        travel_time_to_start_point = q[1]

        # すでに探索済みの座標であれば飛ばす
        if start_point in checked_coordinates:
            continue
        # そうでなければ探索済みマーク
        else:
            checked_coordinates.append(start_point)

        # 次の移動に使える移動時間
        usable_time_for_next_move =  time_limit - travel_time_to_start_point
        # もう使える移動時間がなかったらその座標からの探索は終わり
        if usable_time_for_next_move <= 0:
            continue

        # 探索対象の座標から近い駅を取得
        for travel_time_to_nearby_station_from_start_point, nearby_station in search_walking_area_stations(api, dataset, origin, usable_time_for_next_move, transit_types):
            # 検索した近場の駅が探索済みなら飛ばす
            if nearby_station in checked_stations:
                continue
            # 探査済みチェック
            else:
                checked_stations.append(nearby_station)
            # 近場の駅までの移動時間(探索開始地点までの時間+探索開始地点から，その近場の駅までの移動時間)が，
            # 時間制限に収まるようであればキューに入れる
            travel_time_to_nearby_station = travel_time_to_start_point+travel_time_to_nearby_station_from_start_point
            if travel_time_to_nearby_station <= time_limit:
                # 時間以内に辿り着ける駅
                # 次の探索開始地点とする
                queue.append((nearby_station.geometry.calc_mean(), travel_time_to_nearby_station))
                reachable_stations.append(StationWithTravelTime(station=nearby_station, travel_time=travel_time_to_nearby_station))


    return reachable_stations


def get_reachable_stations3(
        api: MapBoxApi,
        dataset: dict[TransitType, list[Station]],
        origin: Coordinate,
        time_limit: int,
        transit_types: list[TransitType]) -> list[StationWithTravelTime]:
    # 駒込->巣鴨，新宿->巣鴨，のように巣鴨が2階キューに入ってしまうことがある．
    # これを実行時にチェックするためのリスト
    checked_stations: list[Station] = []
    # 探索のためのキュー
    queue: deque[StationWithTravelTime] = deque([])
    # 結果
    reachable_stations: list[StationWithTravelTime] = []

    # 初回入力は座標なので，最初だけループ外で近くの駅を取得する
    _init_nearby_stations = search_walking_area_stations(api, dataset, origin, time_limit, transit_types)
    init_nearby_stations: list[StationWithTravelTime] = list(map(lambda t: StationWithTravelTime(station=t[1], travel_time=t[0]), _init_nearby_stations))
    queue.extend(init_nearby_stations)

    while len(queue) > 0:
        # キューから探索スタート地点とそこまでの移動時間を取得
        q = queue.popleft()
        start_station = q.station
        travel_time_to_start_station = q.travel_time

        # 探索済みの駅だったら飛ばす
        if start_station in checked_stations:
            continue
        # そうでなければ探索済みに
        else:
            checked_stations.append(start_station)

        # 時間以内に移動できるかチェック
        if 0 <= travel_time_to_start_station <= time_limit:
            reachable_stations.append(StationWithTravelTime(start_station, travel_time_to_start_station))
        # できない場合，更なる探索は不要なので飛ばす
        else:
            continue

        # 次の移動に使える移動時間
        usable_time_for_next_move =  time_limit - travel_time_to_start_station
        # もう使える移動時間がなかったらその座標からの探索は終わり
        if usable_time_for_next_move <= 0:
            continue

        # 探索対象の駅から近い駅を取得
        for travel_time_to_nearby_station_from_start_station, nearby_station in search_walking_area_stations(api, dataset, start_station.geometry.calc_mean(), usable_time_for_next_move, transit_types):
            # 次の探索候補
            if travel_time_to_nearby_station_from_start_station < 0:
                continue
            travel_time_to_nearby_station = travel_time_to_start_station + travel_time_to_nearby_station_from_start_station
            queue.append(StationWithTravelTime(station=nearby_station, travel_time=travel_time_to_nearby_station))
        # 同じ路線の駅探すよ
        for travel_time_to_same_line_station_from_start_station, same_line_station in get_same_line_or_route_stations_with_time(start_station, dataset, usable_time_for_next_move):
            if travel_time_to_same_line_station_from_start_station < 0:
                continue
            travel_time_to_same_line_station = travel_time_to_start_station + travel_time_to_same_line_station_from_start_station
            queue.append(StationWithTravelTime(station=same_line_station, travel_time=travel_time_to_same_line_station))

    return reachable_stations