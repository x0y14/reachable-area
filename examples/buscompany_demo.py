from lib.geometry import *
from lib.busstop import *
from lib.yahoo_transit import *
from lib.mapbox import *
from defines import *
from lib.busroute import *
from lib.buscompany import *


def main():
    _routes = create_bus_routes_from_stops(KAIT_SCHOOL_ZONE_BUS_STOPS)
    routes = [_routes[key] for key in _routes.keys()]
    company = BusCompany(id="k", routes=routes, stops=KAIT_SCHOOL_ZONE_BUS_STOPS)
    r = company.get_routes_pass_through_bus_stops([routes[0].stops[0], routes[0].stops[1]])
    print(len(r))


if __name__ == "__main__":
    main()
