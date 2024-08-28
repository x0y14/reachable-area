from enum import IntEnum

import requests

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

        params["access_token"] = self.access_token

        result = requests.get(url=url, params=params)
        return result.json()
