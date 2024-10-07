import csv

import folium
import requests
from django.views.generic import TemplateView
from .forms import SearchForm
from django.shortcuts import render

# fmt: off
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../backend"))
from engine.transit_type import *
# fmt: on

MAPBOX_ATTR = """© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> ©
<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>
<strong
  ><a href="https://labs.mapbox.com/contribute/" target="_blank"
    >Improve this map</a
  ></strong
>"""


class HomeView(TemplateView):
    template_name = "index.html"

    async def get(self, request, *args, **kwargs):
        # 出発地点選択肢の追加
        # points = []
        with open("../dataset/summaries/points.csv", "r") as f:
            reader = csv.reader(f)
            points = list(reader)
        form = SearchForm(data_list=points)

        # 地図の追加
        f = folium.Figure(width="100%", height="50%")
        m = folium.Map(
            location=[35.4861002, 139.3399782],
            zoom_start=14,
            tiles="https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",
            attr=f"出典: 国土地理院ウェブサイト・地理院タイル・標準地図 {MAPBOX_ATTR}",
        )
        f.add_child(m)

        # もし出発地点が選択されてたら地図にプロット
        base_point = request.GET.get("base_point")
        wa_10 = request.GET.get("walk_area_10_minutes")
        wa_20 = request.GET.get("walk_area_20_minutes")
        wa_30 = request.GET.get("walk_area_30_minutes")
        walk_within_minutes = []
        if wa_10 is not None:
            walk_within_minutes.append(10)
        if wa_20 is not None:
            walk_within_minutes.append(20)
        if wa_30 is not None:
            walk_within_minutes.append(30)

        # allow_transit_types = request.GET.get("allow_transit_types")
        # walk_within_minutes
        if (base_point is None) or (base_point == ""):
            f.render()
            return render(
                request,
                "index.html",
                {"map": f, "form": form, "base_point": "No data"},
            )

        search_result = requests.get(
            "http://127.0.0.1:8000/search3",
            params={
                "base_point": base_point,
                "allow_transit_types": [0, 1, 2],  # TODO: fix
                "walk_within_minutes": walk_within_minutes,  # TODO: fix
            },
        )
        if search_result.status_code != 200:
            return render(
                request,
                "index.html",
                {
                    "map": f,
                    "form": form,
                    "base_point": "No data",
                },
            )

        # 検索でbase_pointとした場所を赤ピンで表示
        if "geometry" in search_result.json()["base_point"]:
            geometry = search_result.json()["base_point"]["geometry"]
            folium.Marker(
                location=[
                    geometry["coordinates"][0]["lat"],
                    geometry["coordinates"][0]["lng"],
                ],
                icon=folium.Icon(color="red"),
            ).add_to(m)
        # base_pointを経由する駅を青ピンで表示
        if "stations" in search_result.json():
            for station in search_result.json()["stations"]:
                geometry = station["geometry"]
                folium.Marker(
                    location=[
                        geometry["coordinates"][0]["lat"],
                        geometry["coordinates"][0]["lng"],
                    ],
                    icon=folium.Icon(color="blue"),
                ).add_to(m)

        # search_result.json()["areas"] ->
        # [ 10の結合済みエリアdict, 20の結合済みエリアdict, 30結合済みのエリアdict ]みたいな形で帰ってくる
        if "areas" in search_result.json():
            for area in search_result.json()["areas"]:
                folium.GeoJson(area).add_to(m)

        f.render()

        return render(
            request,
            "index.html",
            {"map": f, "form": form, "base_point": request.GET.get("base_point")},
        )
