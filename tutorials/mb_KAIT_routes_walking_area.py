import json
import os

import folium
from dotenv import load_dotenv
import geopandas

from lib.mapbox import MapBoxApi, IsochroneProfile
from lib.bus import *
from lib.geometry import *


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

    # バス停ファイル読み込み
    kanagawa_bus_stops_geojson = None
    with open("../dataset/busstpos/kanagawa/P11-22_14.geojson") as f:
        kanagawa_bus_stops_geojson = json.load(f)
    kanagawa_bus_stops = get_busstops_from_geojson(kanagawa_bus_stops_geojson)

    # 神工大を通るバス停をリストアップ
    kait_through_busstops: list[BusStop] = []  # 神工大を通るバス停リスト
    for kanagawa_bus_stop in kanagawa_bus_stops:
        if ("神奈川中央" in kanagawa_bus_stop.group and  # 運営会社の名前に「神奈川中央」を含む入っている
                is_include(kanagawa_bus_stop.routes, DIRECT_KAIT_ROUTE + THROUGH_KAIT_ROUTE)):  # 神工大駅、神工大前駅を通る路線に属する
            kait_through_busstops.append(kanagawa_bus_stop)

    # 神工大を通るバス停のループ
    geo_data_frames = []
    for kait_through_busstop in kait_through_busstops:
        # 各バス停から徒歩10,20,30分圏内を取得
        area_walking_10_20_30_from_busstop = mapbox.get_isochrone(
            prof=IsochroneProfile.Walking,
            geo=kait_through_busstop.geometry,
            contours_minutes=[10, 20, 30],
        )

        gdf = geopandas.read_file(area_walking_10_20_30_from_busstop, driver='GeoJSON')
        geo_data_frames.append(gdf)

        # バス停ピンを描画
        pin_icon = None
        if kait_through_busstop.name in ["神奈川工科大学", "神奈川工科大学前"]:  # 神工大の駅なら赤
            pin_icon = folium.Icon(color="red", prefix="fa", icon="school")
        else:  # それ以外は青
            pin_icon = folium.Icon(color="blue", prefix="fa", icon="bus")
        folium.Marker(location=kait_through_busstop.geometry.folium_coordinate(), icon=pin_icon).add_to(folium_map)

    # 徒歩10,20,30分圏内エリアの結合
    result_geo_data_frame = geo_data_frames[0]
    for geo_data_frame in geo_data_frames[1:]:
        result_geo_data_frame.geometry.join(geo_data_frame)


    folium_map.save('mmb_KAIT_routes_walking_area.html')


if __name__ == "__main__":
    main()
