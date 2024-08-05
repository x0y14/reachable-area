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
    return geodesic(tuple(c1.to_geopy()), tuple(c2.to_geopy())).m


@dataclasses.dataclass
class Geometry:
    Type: str
    Coordinates: list[Coordinate]

    def __str__(self):
        return f'{{ "type": {self.Type}, "coordinates": [ {", ".join([str(x) for x in self.Coordinates]) } ] }}'

    def calc_mean_geojson(self) -> list[float]:
        lngs: list[float] = []
        lats: list[float] = []
        for coord in self.Coordinates:
            lng, lat = coord.to_geojson()
            lngs.append(lng)
            lats.append(lat)
        return [statistics.fmean(lngs), statistics.fmean(lats)]

    def calc_mean_reverse_geojson(self) -> list[float]:
        lng, lat = self.calc_mean_geojson()
        return [lat, lng]


def load(d: dict) -> Geometry:
    g_type = d["type"]
    g_coordinates: list[Coordinate] = []

    coordinates = d["coordinates"][0]
    for coord in coordinates:
        g_coordinates.append(Coordinate(Lng=coord[0], Lat=coord[1]))

    return Geometry(Type=g_type, Coordinates=g_coordinates)
