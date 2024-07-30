import dataclasses

from lib.busstop import BusStop
from lib.yahoo_transit import *


@dataclasses.dataclass
class BusRoute:
    id: str
    stops: list[BusStop]

    def register_stop(self, stop: BusStop):
        if self.id not in stop.routes:
            raise Exception(f"登録を試みたバス停:{stop.name}は、路線:{self.id}を通りません")

        _s_names = [lambda x: x.name, self.stops]
        if stop.name in _s_names:
            raise Exception(f"登録を試みたバス停:{stop.name}と同名のバス停が、既に路線:{self.id}に登録されています。")
        self.stops.append(stop)

    # def get_ride_infos(self, from_stop_name: str, to_stop_name: str) -> list[dict]:
    #     if from_stop_name == to_stop_name:
    #         raise Exception(f"同名のバス停間の乗車情報を取得することはできません")
    #     from_stop = None
    #     to_stop = None
    #     for stop in self.stops:
    #         if stop.name == from_stop_name:
    #             from_stop = stop
    #         if stop.name == to_stop_name:
    #             to_stop = stop
    #     if from_stop is None or to_stop is None:
    #         raise Exception(f"{from_stop_name}または{to_stop_name}のいずれかの駅は登録されていません")
    #
    #     return get_route_yahoo_transit(from_stop, to_stop)


def create_bus_routes_from_stops(bus_stops: list[BusStop]) -> dict[str, BusRoute]:
    routes: dict[str, BusRoute] = {}
    for stop in bus_stops:
        for route_id in stop.routes:
            if route_id in routes:
                routes[route_id].register_stop(stop)
            else:
                routes[route_id] = BusRoute(route_id, [stop])

    return routes
