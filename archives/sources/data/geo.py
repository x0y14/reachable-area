import dataclasses
import statistics

from geopy.distance import geodesic


@dataclasses.dataclass
class Coordinate:
    Lng: float
    Lat: float

    def __str__(self):
        return f"[{self.Lng}, {self.Lat}]"  # GeoJson Format

    def to_geojson(self) -> list[float]:
        return [self.Lng, self.Lat]

    def to_reverse_geojson(self) -> list[float]:
        return [self.Lat, self.Lng]

    def to_folium(self) -> list[float]:
        return self.to_reverse_geojson()

    def to_geopy(self) -> list[float]:
        return self.to_reverse_geojson()


def calc_distance_m(c1: Coordinate, c2: Coordinate) -> float:
    """注意: 返却される値は、緯度経度を用いた直線最短距離である。 MAPBOX API等で詳細な距離を出す前のフィルターとして用いることを想定している。"""
    return geodesic(tuple(c1.to_geopy()), tuple(c2.to_geopy())).m


@dataclasses.dataclass
class Geometry:
    Type: str
    Coordinates: list[Coordinate]

    def __str__(self):
        return f'{{ "type": {self.Type}, "coordinates": [ {", ".join([str(x) for x in self.Coordinates])} ] }}'

    def calc_mean(self) -> Coordinate:
        """超適当な座標の平均値算出"""
        lngs: list[float] = []
        lats: list[float] = []
        for coord in self.Coordinates:
            lng, lat = coord.to_geojson()
            lngs.append(lng)
            lats.append(lat)
        return Coordinate(Lng=statistics.fmean(lngs), Lat=statistics.fmean(lats))


def load(d: dict) -> Geometry:
    g_type = d["type"]
    g_coordinates: list[Coordinate] = []

    coordinates = d["coordinates"][0]
    for coord in coordinates:
        g_coordinates.append(Coordinate(Lng=coord[0], Lat=coord[1]))

    return Geometry(Type=g_type, Coordinates=g_coordinates)
