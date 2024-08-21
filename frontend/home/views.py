import csv
from dataclasses import replace

import folium
import requests
from django.views.generic import TemplateView
from home.forms import SearchForm
from django.shortcuts import render

# from backend.engine.transit_type import *

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

        from_ = request.GET.get("from_")
        typ = 0
        if from_ != "":
            if "🚃" in from_:
                from_ = str(from_).replace("🚃", "")
                typ = 1
            elif "🚌" in from_:
                from_ = str(from_).replace("🚌", "")
                typ = 2

            search_result = requests.get(
                "http://127.0.0.1:8000/search", params={"from_": from_, "type_": typ}
            )
            if search_result.status_code == 500:
                return render(
                    request,
                    "index.html",
                    {"map": f, "form": form, "from_": request.GET.get("from_")},
                )
            print(search_result.json())
            if "geometry" in search_result.json():
                geometry = search_result.json()["geometry"]
                folium.Marker(
                    location=[
                        geometry["coordinates"][0]["lat"],
                        geometry["coordinates"][0]["lng"],
                    ],
                    # icon=folium.Icon(color="red", prefix="fa", icon="school"),
                ).add_to(m)

        f.render()

        return render(
            request,
            "index.html",
            {"map": f, "form": form, "from_": request.GET.get("from_")},
        )
