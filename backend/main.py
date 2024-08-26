from re import split
from typing import List, Union

from fastapi import FastAPI, Query
from contextlib import asynccontextmanager


from engine import TransitType
from engine.bus import *
from engine.train import *

dataset: dict[str, Union[list[BusStop], list[TrainStation]]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("on start")
    dataset["bus_stops"] = load_stop_data(
        "../dataset/busstpos/kanagawa/P11-22_14.geojson"
    )
    dataset["stations"] = load_station_data(
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
    return dataset["bus_stops"]


@app.get("/search")
async def search(type_: int = 0, from_: str = "", to_: str = ""):
    transit_type = TransitType(type_)

    _from_split = split("/", from_)
    point_name = _from_split[1]

    if transit_type == TransitType.BUS:
        management_companies = _from_split[0].split("・")
        for stop in dataset["bus_stops"]:  # type: BusStop
            # print(stop)
            if (stop.management_groups == management_companies) and (
                stop.name == point_name
            ):
                return stop.as_dict()
    elif transit_type == TransitType.TRAIN:
        line = _from_split[0]
        for station in dataset["stations"]:  # type: TrainStation
            if (station.line == line) and (station.name == point_name):
                return station.as_dict()

    return {"from_": from_, "to_": to_}


@app.get("/search2")
async def search2(
    base_point: str = Query(),
    allow_transit_types: List[int] = Query(),
):
    _base_point = base_point.split("/")
    transit_type = TransitType(int(_base_point[0]))
    management_group_or_line = _base_point[1]
    stop_name = _base_point[2]

    if transit_type == TransitType.BUS:
        management_companies = management_group_or_line.split("・")
        target_base_stop = None
        for stop in dataset["bus_stops"]:  # type: BusStop
            if (stop.management_groups == management_companies) and (
                stop.name == stop_name
            ):
                target_base_stop = stop

    return {"base_point": base_point, "allow_transit_types": allow_transit_types}
