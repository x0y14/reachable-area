import csv

import folium
from django.views.generic import TemplateView
from app.forms import FormForm
from django.shortcuts import render
from django.apps import apps

# def country_form(request):
#     # instead of hardcoding a list you could make a query of a model, as long as
#     # it has a __str__() method you should be able to display it.
#     # country_list = ["Mexico", "USA", "China", "France", "usa"]
#     points = []
#     with open("scripts/points.csv", "r") as f:
#         reader = csv.reader(f)
#         points = list(reader)
#
#     form = FormForm(data_list=points)
#
#     return render(request, "index.html", {"form": form})
#

MAPBOX_ATTR = """© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> ©
<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>
<strong
  ><a href="https://labs.mapbox.com/contribute/" target="_blank"
    >Improve this map</a
  ></strong
>"""


class AppView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        bus_stops = apps.get_app_config("app").stations
        # 出発地点選択肢の追加
        points = []
        # with open("scripts/points.csv", "r") as f:
        #     reader = csv.reader(f)
        #     points = list(reader)
        form = FormForm(data_list=bus_stops)

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

        f.render()

        return render(
            request,
            "index.html",
            {"map": f, "form": form, "from_": request.GET.get("from_")},
        )

    #
    # def get_context_data(self, **kwargs):
    #     figure = folium.Figure()
    #
    #     # Make the map
    #     map = folium.Map(location=[40.416, -3.70], zoom_start=11, tiles="OpenStreetMap")
    #
    #     map.add_to(figure)
    #     figure.render()
    #     return {"map": figure}
