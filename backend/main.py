from cProfile import label
from re import split
from typing import List, Any

from anyio.from_thread import start_blocking_portal
from fastapi import FastAPI, Query
from contextlib import asynccontextmanager


from engine import TransitType, BusStop, TrainStation
from engine.bus import *
from engine.train import *

dataset: dict[TransitType, list[Station]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("on start")
    dataset[TransitType.BUS] = load_stop_data(
        "../dataset/busstpos/kanagawa/P11-22_14.geojson"
    )
    dataset[TransitType.TRAIN] = load_station_data(
        "../dataset/stations/N02-20_Station.geojson"
    )
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
    walk_within_minutes: int = Query(default=10),
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

    return {"base_point": res, "stations": station_list_as_dict_list(stations)}
