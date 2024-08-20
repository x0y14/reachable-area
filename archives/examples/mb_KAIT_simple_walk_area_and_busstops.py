import json
import os
import folium
from dotenv import load_dotenv
from lib.mapbox import MapBoxApi, IsochroneProfile
from lib.bus import *
from lib.geometry import Geometry

load_dotenv()

KAIT_GEO = Geometry(type="", long=139.3399782, lat=35.4861002)
DIRECT_KAIT_ROUTE = ["厚67"]
THROUGH_KAIT_ROUTE = ["厚07", "厚67", "厚89"]


def is_include(l1: list, l2: list) -> bool:
    for item in l2:
        if item in l1:
            return True
    return False


def main():
    # Mapbox apiの準備
    mapbox = MapBoxApi(os.environ["MAPBOX_API_TOKEN"])
    # 神工大から徒歩10,20,30分のエリアのポリゴンを取得
    result = mapbox.get_isochrone(
        prof=IsochroneProfile.Walking,
        geo=KAIT_GEO,
        contours_minutes=[10, 20, 30],
    )
    isochrone_geojson = result
    # 国土地理院タイルを用いて、神工大を中心とした地図を生成
    folium_map = folium.Map(
        location=KAIT_GEO.folium_coordinate(),
        zoom_start=13,
        tiles="https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",
        attr="出典: 国土地理院ウェブサイト・地理院タイル・標準地図"
    )
    # 徒歩10,20,30分のポリゴンを地図に描画
    for feature in isochrone_geojson["features"]:
        folium.GeoJson(
            feature["geometry"],
            style_function=lambda x: feature["properties"]
        ).add_to(folium_map)

    # 神工大駅、神工大前駅を通るバス路線の全てのバス停をプロット
    # バス停ファイル読み込み
    kanagawa_bus_stops_geojson = None
    with open("../dataset/busstpos/kanagawa/P11-22_14.geojson") as f:
        kanagawa_bus_stops_geojson = json.load(f)
    kanagawa_bus_stops = get_busstops_from_geojson(kanagawa_bus_stops_geojson)
    # バス停描画
    for kanagawa_bus_stop in kanagawa_bus_stops:
        if ("神奈川中央" in kanagawa_bus_stop.group and
                is_include(kanagawa_bus_stop.routes, DIRECT_KAIT_ROUTE+THROUGH_KAIT_ROUTE)):  # かなちゅうバスのみ かつ KAITを通る
            if kanagawa_bus_stop.name in ["神奈川工科大学", "神奈川工科大学前"]:
                folium.Marker(location=kanagawa_bus_stop.geometry.folium_coordinate(), icon=folium.Icon(color='red')).add_to(folium_map)
            else:
                folium.Marker(location=kanagawa_bus_stop.geometry.folium_coordinate()).add_to(folium_map)

    # 地図保存
    folium_map.save('kait_area_with_busstops.html')


if __name__ == "__main__":
    main()
