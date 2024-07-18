import dataclasses


@dataclasses.dataclass
class Geometry:
    type: str
    lat: float
    long: float

    def folium_coordinate(self) -> list[float]:
        return [self.lat, self.long]

    def geojson_coordinate(self) -> list[float]:
        return [self.long, self.lat]

# Sample
# Geometry(type='Point', coordinates=[139.5967436356555, 35.46710563861377])
