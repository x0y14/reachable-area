# 参考: [foliumの基本的な使い方とオープンデータ活用](https://qiita.com/Kumanuron-1910/items/12ce7aa02922927de2f4)
import json

import folium

from main import get_busstops_from_geojson

KAIT_COORDINATES = [35.4861002,139.3399782]


def main():
    # [データ読み込み]
    # バス停
    kanagawa_bus_stops_geojson = None
    with open("../dataset/busstpos/kanagawa/P11-22_14.geojson") as f:
        kanagawa_bus_stops_geojson = json.load(f)

    # [データの加工]
    # バス停
    kanagawa_bus_stops = get_busstops_from_geojson(kanagawa_bus_stops_geojson)

    # バス停の地図用意
    folium_map = folium.Map(location=KAIT_COORDINATES, zoom_start=15)
    # バス停をプロット
    for kanagawa_bus_stop in kanagawa_bus_stops:
        if "神奈川中央" in kanagawa_bus_stop.group: # かなちゅうバスのみ
            print(kanagawa_bus_stop)
            folium.Marker(location=kanagawa_bus_stop.geometry.coordinates).add_to(folium_map)
    # 地図保存
    folium_map.save('busstop_ploted_kait.html')
    # folium_map


if __name__ == "__main__":
    main()
