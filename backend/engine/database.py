import json
import sqlite3
import dataclasses
from typing import Optional

from engine import Station


def get_conn(dbpath: str) -> sqlite3.Connection:
    conn = sqlite3.connect(dbpath)
    return conn


@dataclasses.dataclass
class InsertRouteReq:
    is_bus_route: bool

    from_: Station
    to_: Station

    time_required: int
    transfer: int
    fare: int
    distance: int

@dataclasses.dataclass
class GetRoutesReq:
    is_bus_route:bool
    from_:Station
    to_:Station


def insert_route(conn: sqlite3.Connection, req: InsertRouteReq):
    cur = conn.cursor()
    cur.execute(
        """insert into 
        routes (is_bus_route, from_, to_, time_required, transfer, fare, distance)
         VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (1 if req.is_bus_route is True else 0, req.from_.name, req.to_.name, req.time_required, req.transfer, req.fare, req.distance)
    )
    print(f"receive insert request: {req.from_.name}->{req.to_.name}")
    conn.commit()
    return {"time_required": req.time_required, "transfer": req.transfer, "fare": req.fare, "distance": req.distance}

def get_routes(conn: sqlite3.Connection, req: GetRoutesReq) -> list[dict]:
    cur = conn.cursor()
    cur.execute("""select * from routes where is_bus_route=? and from_=? and to_=?""", (1 if req.is_bus_route is True else 0, req.from_.name, req.to_.name))

    routes = []
    for record in cur.fetchall():
        # id = record[0]
        # is_bus_route = record[1]
        # from_ = record[2]
        # to_ = record[3]
        time_required = record[4]
        transfer = record[5]
        fare = record[6]
        distance = record[7]
        routes.append(
            {
                "time_required": int(time_required),
                "transfer": int(transfer),
                "fare": int(fare),
                "distance": int(distance)
            }
        )
    return routes

def insert_isochrones(conn: sqlite3.Connection, request_param: dict, isochrone_from_mapbox: dict) -> None:
    cur = conn.cursor()
    cur.execute("""insert into isochrones (web_request, web_response) values (?, ?);""", [json.dumps(request_param), json.dumps(isochrone_from_mapbox)])
    conn.commit()

def get_isochrones(conn: sqlite3.Connection, request_param: dict) -> Optional[dict]:
    cur = conn.cursor()
    cur.execute("""select web_response from isochrones where web_request=?;""", [json.dumps(request_param)])
    response_json = cur.fetchone()

    if response_json:
        return json.loads(response_json[0])
    return None