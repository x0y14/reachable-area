import dataclasses


@dataclasses.dataclass
class Geometry:
    type: str
    coordinates: list[float]


# Sample
# Geometry(type='Point', coordinates=[139.5967436356555, 35.46710563861377])
