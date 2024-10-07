import os
from re import split
from typing import List, Any

import folium
import geopandas
from django.utils.dateparse import time_re
from shapely.ops import unary_union

from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from engine import TransitType, BusStop, TrainStation, prepare_empty_lists, get_stations_with_time
from engine.bus import *
from engine.mapbox import MapBoxApi, IsochroneProfile, concat_isochrones
from engine.train import *

load_dotenv()

dataset: dict[TransitType, list[Station]] = {}
mapbox_api: MapBoxApi = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("on start")
    dataset[TransitType.BUS] = load_stop_data(
        "../dataset/busstops/kanagawa/P11-22_14.geojson"
    )
    dataset[TransitType.TRAIN] = load_station_data(
        "../dataset/stations/N02-20_Station.geojson"
    )

    global mapbox_api
    mapbox_api = MapBoxApi(os.getenv("MAPBOX_API_TOKEN"))

    yield
    print("on end")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/bus")
def read_bus_stops():
    return dataset[TransitType.BUS]


@app.get("/search")
async def search(type_: int = 0, from_: str = "", to_: str = ""):
    transit_type = TransitType(type_)

    _from_split = split("/", from_)
    point_name = _from_split[1]

    if transit_type == TransitType.BUS:
        management_companies = _from_split[0].split("・")
        for stop in dataset[TransitType.BUS]:  # type: BusStop
            # print(stop)
            if (stop.management_groups == management_companies) and (
                stop.name == point_name
            ):
                return stop.as_dict()
    elif transit_type == TransitType.TRAIN:
        line = _from_split[0]
        for station in dataset[TransitType.TRAIN]:  # type: TrainStation
            if (station.line == line) and (station.name == point_name):
                return station.as_dict()

    return {"from_": from_, "to_": to_}


def _include(a: list[str], b: list[str]) -> bool:
    for a_content in a:
        if a_content in b:
            return True
    return False


def get_same_line_route_stations(station: Station) -> list[Station]:
    stations: list[Station] = []

    if station.transit_type == TransitType.BUS:
        for stop in dataset[TransitType.BUS]:
            if (
                (stop.management_groups == station.management_groups)
                and (_include(station.line_routes, stop.line_routes))
                and (stop.name != station.name)
            ):
                stations.append(stop)
    elif station.transit_type == TransitType.TRAIN:
        for stat in dataset[TransitType.TRAIN]:
            if (stat.line_routes == station.line_routes) and (
                stat.name != station.name
            ):
                stations.append(stat)

    return stations


def station_list_as_dict_list(stations: list[Station]) -> list[dict[str, Any]]:
    res: list[dict[str, Any]] = []
    for st in stations:
        res.append(st.as_dict())
    return res


@app.get("/search2")
async def search2(
    base_point: str = Query(),
    allow_transit_types: List[int] = Query(),
    walk_within_minutes: List[int] = Query(),
):
    # 文字列の分解
    _base_point = base_point.split("/")
    transit_type = TransitType(int(_base_point[0]))  # TransitTypeに準拠
    management_group_or_line = _base_point[
        1
    ]  # 神奈川中央交通（株）だったり中央線みたいなのが入る
    station_name = _base_point[2]  # 市役所前とか新宿みたいに駅名

    target_base_stop = None
    if transit_type == TransitType.BUS:
        management_companies = management_group_or_line.split("・")
        for stop in dataset[TransitType.BUS]:
            if (stop.management_groups == management_companies) and (
                stop.name == station_name
            ):
                target_base_stop = stop
    elif transit_type == TransitType.TRAIN:
        line = [management_group_or_line]
        for station in dataset[TransitType.TRAIN]:
            if (station.line_routes == line) and (station.name == station_name):
                target_base_stop = station

    res = {}  # <- ラムダ式だと不可解な挙動する
    stations: list[Station] = []
    if target_base_stop is not None:
        res = target_base_stop.as_dict()
        stations = get_same_line_route_stations(target_base_stop)

    # 距離ごとに分けて格納する
    walk_areas = prepare_empty_lists(len(walk_within_minutes))
    walk_area_polygons = []
    for stat in [target_base_stop, *stations]:
        area_features_collection = mapbox_api.get_isochrone(
            prof=IsochroneProfile.Walking,
            coordinate=stat.geometry.Coordinates[0],
            contours_minutes=walk_within_minutes,
        )
        # print(area_features_collection)
        gdf = geopandas.GeoDataFrame.from_features(area_features_collection)
        # おおきいじゅんで入っているぽい
        # 小さい順に直すので
        for i in range(len(walk_within_minutes)):
            walk_areas[i].append(gdf.geometry[(len(walk_within_minutes) - 1) - i])

    for walk_area in walk_areas:
        walk_area_polygons.append(geopandas.GeoSeries(unary_union(walk_area)).to_json())

    # area = mapbox_api.get_isochrone(
    #     prof=IsochroneProfile.Walking,
    #     coordinate=target_base_stop.geometry.Coordinates[0],
    #     contours_minutes=walk_within_minutes,
    # )
    # walk_areas.append(area)

    return {
        "base_point": res,
        "allow_transit_types": allow_transit_types,
        "stations": station_list_as_dict_list(stations),
        "areas": walk_area_polygons,
    }

@app.get("/search3")
async def search3(
        base_point: str = Query(),
        allow_transit_types: List[int] = Query(),
        walk_within_minutes: List[int] = Query(), # 徒歩時間->全体の移動時間に変更する必要あり
):
    # 文字列の分解
    _base_point = base_point.split("/")
    transit_type = TransitType(int(_base_point[0]))  # TransitTypeに準拠
    management_group_or_line = _base_point[1]  # 神奈川中央交通（株）だったり中央線みたいなのが入る
    station_name = _base_point[2]  # 市役所前とか新宿みたいに駅名
    # ベースの駅を探す
    target_base_stop = None
    if transit_type == TransitType.BUS:
        management_companies = management_group_or_line.split("・")
        for stop in dataset[TransitType.BUS]:
            if (stop.management_groups == management_companies) and (
                    stop.name == station_name
            ):
                target_base_stop = stop
    elif transit_type == TransitType.TRAIN:
        line = [management_group_or_line]
        for station in dataset[TransitType.TRAIN]:
            if (station.line_routes == line) and (station.name == station_name):
                target_base_stop = station

    reachable_areas = []
    stations = []
    for travel_time_min in walk_within_minutes:
        isochrones = []
        for time_req, near_station in get_stations_with_time(target_base_stop, dataset, travel_time_min):
            stations.append(near_station)
            contour = travel_time_min - time_req
            if contour < 1:
                contour = 1
            if 60 < contour:
                contour = 60
            isochrone_feature_collection = mapbox_api.get_isochrone(
                prof=IsochroneProfile.Walking,
                coordinate=near_station.geometry.calc_mean(),
                contours_minutes=[contour]
            )
            isochrones.append(isochrone_feature_collection)
        reachable_areas.append(
            concat_isochrones(isochrones).to_json()
        )

    return {
        "base_point": target_base_stop.as_dict(),
        "allow_transit_types": allow_transit_types,
        "stations": station_list_as_dict_list(stations),
        "areas": reachable_areas,
    }
