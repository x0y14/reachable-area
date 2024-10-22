from engine.mapbox import MapBoxApi, IsochroneProfile
from engine.train import *
import geopandas
from shapely.geometry import Point


def search_nearby_walking_distance_stations(
        api: MapBoxApi,
        dataset: dict[TransitType, list[Station]],
        coordinate: Coordinate,
        time_limits: list[int],
        transit_types: list[TransitType]
) -> dict[int, list[Station]]:
    nearby_stations: dict[int, list[Station]] = {tl: [] for tl in time_limits}
    walking_areas_with_time_limit: dict[int, geopandas.GeoDataFrame] = {}

    # MapboxApiを用いてisochroneを取得
    isochrones: dict = api.get_isochrone(
        prof=IsochroneProfile.Walking,
        coordinate=coordinate,
        contours_minutes=time_limits,
    )

    # Isochroneの加工
    for time_limit in time_limits:
        isochrone: dict = [isochrone for isochrone in isochrones["features"] if isochrone["properties"]["contour"] == time_limit][0]
        isochrone_gpd = geopandas.GeoDataFrame.from_features(
            {"features": [isochrone], "type": "FeatureCollection"}
        )
        walking_areas_with_time_limit[time_limit] = isochrone_gpd


    # チェック対象を確認
    candidates: list[Station] = []
    if TransitType.BUS in transit_types:
        candidates += dataset[TransitType.BUS]
    if TransitType.TRAIN in transit_types:
        candidates += dataset[TransitType.TRAIN]

    # チェック
    for candidate in candidates:
        candidate_coord = candidate.geometry.calc_mean()
        candidate_point = Point(candidate_coord.Lng, candidate_coord.Lat)
        for time_limit, walking_area in walking_areas_with_time_limit.items():
            is_include = bool(walking_area.contains(candidate_point)[0])
            if is_include:
                nearby_stations[time_limit].append(candidate)

    return nearby_stations


# search_nearby_walking_distance_stationsのisochroneを既に持ってる場合の版
def get_stations_contain_area(
        dataset: dict[TransitType, list[Station]],
        isochrone: dict,
        transit_types: list[TransitType]
) -> list[Station]:
    nearby_stations: list[Station] = []

    isochrone_gpd = geopandas.GeoDataFrame.from_features(isochrone)

    # チェック対象を確認
    candidates: list[Station] = []
    if TransitType.BUS in transit_types:
        candidates += dataset[TransitType.BUS]
    if TransitType.TRAIN in transit_types:
        candidates += dataset[TransitType.TRAIN]

    for candidate in candidates:
        candidate_coord = candidate.geometry.calc_mean()
        candidate_point = Point(candidate_coord.Lng, candidate_coord.Lat)
        is_include = bool(isochrone_gpd.contains(candidate_point)[0])
        if is_include:
            nearby_stations.append(candidate)

    return nearby_stations
