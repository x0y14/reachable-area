# 参考: [foliumの基本的な使い方とオープンデータ活用](https://qiita.com/Kumanuron-1910/items/12ce7aa02922927de2f4)
import json
import folium
from lib.bus import *


KAIT_COORDINATES = [35.4861002,139.3399782]
DIRECT_KAIT_ROUTE = ["厚67"]
THROUGH_KAIT_ROUTE = ["厚07", "厚67", "厚89"]

# Sample
# BusStop(name='神奈川工科大学', group='神奈川中央交通（株）', routes=['厚67'], geometry=Geometry(type='Point', coordinates=[35.48634079963154, 139.34069452271203]))
# BusStop(name='神奈川工科大学前', group='神奈川中央交通（株）', routes=['厚07', '厚67', '厚89'], geometry=Geometry(type='Point', coordinates=[35.48517315672544, 139.34089918555708]))


# l1にl2のいずれかが含まれるかチェック
def is_include(l1: list, l2: list) -> bool:
    for item in l2:
        if item in l1:
            return True
    return False


def main():
    # [データ読み込み]
    # バス停
    kanagawa_bus_stops_geojson = None
    with open("../dataset/busstpos/kanagawa/P11-22_14.geojson") as f:
        kanagawa_bus_stops_geojson = json.load(f)

    # [データの加工]
    # バス停
    kanagawa_bus_stops = get_busstops_from_geojson(kanagawa_bus_stops_geojson)

    # [描画]
    # バス停の地図用意
    folium_map = folium.Map(location=KAIT_COORDINATES, zoom_start=9)
    # バス停をプロット
    for kanagawa_bus_stop in kanagawa_bus_stops:
        if ("神奈川中央" in kanagawa_bus_stop.group and
                is_include(kanagawa_bus_stop.routes, DIRECT_KAIT_ROUTE+THROUGH_KAIT_ROUTE)):  # かなちゅうバスのみ かつ KAITを通る
            print(kanagawa_bus_stop)
            if kanagawa_bus_stop.name in ["神奈川工科大学", "神奈川工科大学前"]:
                folium.Marker(location=kanagawa_bus_stop.geometry.coordinates, icon=folium.Icon(color='red')).add_to(folium_map)
            else:
                folium.Marker(location=kanagawa_bus_stop.geometry.coordinates).add_to(folium_map)
    # 地図保存
    folium_map.save('kait_routes.html')
    # folium_map


if __name__ == "__main__":
    main()
