from lib.busstop import BusStop
from lib.geometry import Geometry


def convert_busstop_geojson_to_dataclass(geojson: dict) -> BusStop:
    coord_long = geojson["geometry"]["coordinates"][0]
    coord_lat = geojson["geometry"]["coordinates"][1]
    geo = Geometry(
        type=geojson["geometry"]["type"],
        long=coord_long,
        lat=coord_lat,
    )
    routes = str(geojson["properties"]["P11_003_01"]).split(",")
    busstop = BusStop(
        name=geojson["properties"]["P11_001"],
        group=geojson["properties"]["P11_002"],
        routes=routes,
        geometry=geo,
    )
    return busstop


def get_busstops_from_geojson(geojson: dict) -> list[BusStop]:
    busstops = []
    for feature in geojson["features"]:
        busstops.append(convert_busstop_geojson_to_dataclass(feature))
    return busstops
