import dataclasses

from lib.busstop import BusStop
from lib.busroute import BusRoute
from lib.yahoo_transit import *


@dataclasses.dataclass
class BusCompany:
    id: str
    routes: list[BusRoute]
    stops: list[BusStop]

    def get_routes_pass_through_bus_stops(self, stops: list[BusStop]) -> list[BusRoute]:
        result: list[BusRoute] = []

        for route in self.routes:
            # if set(stops) <= set(route.stops):
            #     result.append(route)
            left = len(stops)
            for stop in stops:
                if stop in route.stops:
                    left -= 1
            if left == 0:
                result.append(route)

        return result

    def get_ride_infos(self, from_stop_name: str, to_stop_name: str) -> list[dict]:
        if from_stop_name == to_stop_name:
            raise Exception(f"同名のバス停間の乗車情報を取得することはできません")
        from_stop = None
        to_stop = None
        for stop in self.stops:
            if stop.name == from_stop_name:
                from_stop = stop
            if stop.name == to_stop_name:
                to_stop = stop
        if from_stop is None or to_stop is None:
            raise Exception(f"{from_stop_name}または{to_stop_name}のいずれかの駅は登録されていません")

        routes = self.get_routes_pass_through_bus_stops([from_stop, to_stop])
        if len(routes) == 0:
            raise Exception(f"{from_stop_name}と{to_stop_name}の両方を通過する路線が存在しません")

        return get_route_yahoo_transit(from_stop, to_stop)
