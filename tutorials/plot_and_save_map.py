# 参考: [foliumの基本的な使い方とオープンデータ活用](https://qiita.com/Kumanuron-1910/items/12ce7aa02922927de2f4)

import folium


KAIT_COORDINATES = [35.4861002, 139.3399782]

KAIT_BUS_STOP = [35.48634079963154, 139.34069452271203]

def main():
    # 地図生成
    folium_map = folium.Map(location=KAIT_COORDINATES, zoom_start=15)
    folium_map.add_child(folium.Marker(location=KAIT_BUS_STOP))

    # 地図保存
    folium_map.save('kait.html')
    # folium_map


if __name__ == "__main__":
    main()
