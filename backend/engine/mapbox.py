import os
from enum import IntEnum

import requests
from typing import Any
import geopandas
from shapely.geometry import Point
from shapely.ops import unary_union

from definitions import PROJECT_ENGINE_DIR
from . import get_conn
from .database import get_isochrones, insert_isochrones
from .geo import *


class IsochroneProfile(IntEnum):
    DrivingTraffic = 1
    Driving = 2
    Walking = 3
    Cycling = 4


def isochrone_to_str(iso_prof: IsochroneProfile) -> str:
    if iso_prof == IsochroneProfile.DrivingTraffic:
        return "mapbox/driving-traffic"
    elif iso_prof == IsochroneProfile.Driving:
        return "mapbox/driving"
    elif iso_prof == IsochroneProfile.Walking:
        return "mapbox/walking"
    elif iso_prof == IsochroneProfile.Cycling:
        return "mapbox/cycling"


def concat_isochrones_per_contour(isochrones: list[dict[Any, Any]]) -> dict[int, dict]:
    result: dict[int, dict[Any, Any]] = {}  # int -> time_contour -> ["features"]["properties"]["contour"]
    for feature_collection in isochrones:
        gdf = geopandas.GeoDataFrame.from_features(feature_collection)
        for feature in gdf.iterfeatures():
            contour = feature["properties"]["contour"]
            # init
            if contour not in result:
                result[contour] = feature
            else:
                result[contour] = geopandas.GeoSeries(unary_union([result[contour], feature])).to_dict()

    return result

def concat_isochrones(isochrones: list[dict[Any, Any]]) -> geopandas.GeoSeries:
    gdf_geometries = []
    for feature_collection in isochrones:
        gdf = geopandas.GeoDataFrame.from_features(feature_collection)
        for gdf_geometry in gdf.geometry:
            gdf_geometries.append(gdf_geometry)
    return geopandas.GeoSeries(unary_union(gdf_geometries))


class MapBoxApi:
    def __init__(self, access_token):
        self.access_token = access_token

    def get_isochrone(
        self,
        prof: IsochroneProfile,
        coordinate: Coordinate,
        contours_minutes: list[int] = None,
        contours_meters: list[int] = None,
        contours_colors: list[str] = None,
        polygons: bool = True,
        denoise: float = 1.0,
        generalize: float = None,
        exclude: list[str] = None,
        depart_at: str = None,
    ):
        # パラメータ準備
        p_isochrone_profile = isochrone_to_str(prof)
        p_center_coordinates = f"{coordinate.Lng},{coordinate.Lat}"

        if contours_minutes is None and contours_meters is None:
            raise Exception(
                "contours_minutes, contours_metersのいずれかを入力してください"
            )
        if contours_minutes is not None and contours_meters is not None:
            raise Exception(
                "contours_minutes, contours_metersのいずれかを入力してください"
            )
        _c = None
        if contours_minutes is not None:
            _c = map(lambda i: str(i), contours_minutes)
        if contours_meters is not None:
            _c = map(lambda i: str(i), contours_meters)
        p_contours = ",".join(_c)

        p_colors = ",".join(contours_colors) if contours_colors is not None else None

        p_polygons = "true" if polygons is True else "false"

        p_denoise = str(denoise)

        p_generalize = str(generalize) if generalize is not None else None

        p_exclude = ",".join(exclude) if exclude is not None else None

        p_depart_at = depart_at

        # リクエストの準備
        url = f"https://api.mapbox.com/isochrone/v1/{p_isochrone_profile}/{p_center_coordinates}"
        params = {}
        if contours_minutes is not None:
            params["contours_minutes"] = p_contours
        else:
            params["contours_meters"] = p_contours
        if p_colors is not None:
            params["contours_colors"] = p_colors
        params["polygons"] = p_polygons
        params["denoise"] = p_denoise
        if p_generalize is not None:
            params["generalize"] = p_generalize
        if p_exclude is not None:
            params["exclude"] = p_exclude
        if p_depart_at is not None:
            params["depart_at"] = p_depart_at

        # CACHEが利用可能か確認
        conn = get_conn(os.path.join(PROJECT_ENGINE_DIR, "cache.db"))
        cached_isochrones = get_isochrones(conn, params)
        if cached_isochrones: # あったので返す
            conn.close()
            return cached_isochrones

        params["access_token"] = self.access_token

        result = requests.get(url=url, params=params)
        if result.status_code!=200:
            raise Exception(f"MAPBOX API ERROR: {result.json()}")

        # キャッシュ挿入
        # アクセストークンは消す
        del params["access_token"]
        insert_isochrones(conn, params, result.json())
        conn.close()

        return result.json()

    # 60分を超えるとMAPBOX APIとISOCHRONEを使用できなくなるため、正確な値ではなく直線距離からの簡易的な計算値になります。
    def get_walking_travel_time(self, coordinate1: Coordinate, coordinate2: Coordinate) -> int:
        walking_distance_areas: dict[int, geopandas.GeoDataFrame] = {}

        contours = [x for x in range(1, 61)]
        contour_quarters = [contours[i:i+4] for i in range(0, len(contours), 4)]

        # ISOCHRONE APIのcontourは同時に4つしか指定できない
        for contour_quarter in contour_quarters:
            isochrones = self.get_isochrone(
                prof=IsochroneProfile.Walking,
                coordinate=coordinate1,
                contours_minutes=contour_quarter
            )
            # Isochroneの加工
            for contour in contour_quarter:
                isochrone: dict = [isochrone for isochrone in isochrones["features"] if isochrone["properties"]["contour"] == contour][0]
                isochrone_gpd = geopandas.GeoDataFrame.from_features(
                    {"features": [isochrone], "type": "FeatureCollection"}
                )
                walking_distance_areas[contour] = isochrone_gpd

        # 60分以内
        for travel_time, walking_distance_area in walking_distance_areas.items():
            point = Point(coordinate2.Lng, coordinate2.Lat)
            is_contain = bool(walking_distance_area.contains(point)[0])
            if is_contain:
                return travel_time

        # 60分以上
        # 直線距離の計算に入ります. 80m = 1分
        distance = calc_distance_m(coordinate1, coordinate2)
        return int(distance / 80)
