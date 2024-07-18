import os
import folium
from dotenv import load_dotenv
from lib.mapbox import MapBoxApi, IsochroneProfile


load_dotenv()
KAIT_COORDINATES_GEO = [139.3399782, 35.4861002]


def main():
    # Mapbox apiの準備
    mapbox = MapBoxApi(os.environ["MAPBOX_API_TOKEN"])
    # 神工大から徒歩10,20,30分のエリアのポリゴンを取得
    result = mapbox.get_isochrone(
        prof=IsochroneProfile.Walking,
        coord=KAIT_COORDINATES_GEO,
        contours_minutes=[10, 20, 30],
    )
    isochrone_geojson = result
    # 国土地理院タイルを用いて、神工大を中心とした地図を生成
    folium_map = folium.Map(
        location=[KAIT_COORDINATES_GEO[1], KAIT_COORDINATES_GEO[0]],
        zoom_start=13,
        tiles="https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png",
        attr="国土地理院"
    )
    # 徒歩10,20,30分のポリゴンを地図に描画
    for feature in isochrone_geojson["features"]:
        folium.GeoJson(
            feature["geometry"],
            style_function=lambda x: feature["properties"]
        ).add_to(folium_map)
    # 地図保存
    folium_map.save('kait_area.html')


if __name__ == "__main__":
    main()
