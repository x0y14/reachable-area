import dataclasses


@dataclasses.dataclass
class Coordinate:
    Lng: float
    Lat: float

    def __str__(self):
        return f"[{self.Lng}, {self.Lat}]"  # GeoJson Format

    def to_geojson(self) -> list[float]:
        return [self.Lng, self.Lat]

    def to_folium(self) -> list[float]:
        return [self.Lat, self.Lng]


@dataclasses.dataclass
class Geometry:
    Type: str
    Coordinates: list[Coordinate]

    def __str__(self):
        return f'{{ "type": {self.Type}, "coordinates": [ {", ".join([str(x) for x in self.Coordinates]) } ] }}'


def load(d: dict) -> Geometry:
    g_type = d["type"]
    g_coordinates: list[Coordinate] = []

    coordinates = d["coordinates"][0]
    for coord in coordinates:
        g_coordinates.append(Coordinate(Lng=coord[0], Lat=coord[1]))

    return Geometry(Type=g_type, Coordinates=g_coordinates)
