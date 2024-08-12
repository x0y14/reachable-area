# 卒研

## 概要

Repo: https://github.com/x0y14/reachable-area

## 環境変数

- `MAPBOX_API_TOKEN` MAPBOXのAccess tokensを貼り付けてください

## データ

**使用している各データは、自ら用意したものでない限りignoreしています。**

### バス停

バス停データは[国土数値情報ダウンロードサイト・バス停留所データ](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P11-v3_0.html)
から取得しています。

| ファイル名             | 設置場所                                        | ダウンロード元             |
|-------------------|---------------------------------------------|---------------------|
| P11-22_14.geojson | dataset/busstpos/kanagawa/P11-22_14.geojson | 神奈川（シェープ、geojson形式） |

### 鉄道駅

鉄道駅のデータは[国土数値情報ダウンロードサイト・鉄道データ](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html)
から取得しています。

| ファイル名                  | 設置場所                                    | ダウンロード元       |
|------------------------|-----------------------------------------|---------------| 
| N02-20_Station.geojson | dataset/stations/N02-20_Station.geojson | 全国・世界測地系・令和2年 |

### 地図タイル

Foliumで表示する一部の地図に国土地理院ウェブサイトが提供する[地理院タイル・標準地図](https://maps.gsi.go.jp/development/ichiran.html#std)
を使用しています。  
`地理院タイル・標準地図`は`基本測量成果`に該当します。  
ただし、本成果品は卒業論文に用いられるものであり、[測量成果ワンストップサービス](https://onestop.gsi.go.jp/onestopservice/navi/nav5-2.html#5-2)
によれば不特定多数への提供に該当しません。  
よって、出典の記載のみを行います。

## 参考文献

- [foliumの基本的な使い方とオープンデータ活用](https://qiita.com/Kumanuron-1910/items/12ce7aa02922927de2f4)
- [【folium】地図のMarkerの色や形・アイコン・タイルを変える](https://chayarokurokuro.hatenablog.com/entry/2020/09/02/212350)
- [Python+folium+openrouteserviceを使う (経路・時間行列・等時線を例に)](https://zenn.dev/takilog/articles/2be029ccd35972)
- [Mapbox の Isochrone API を使用してみた。](https://freedom-tech.hatenablog.com/entry/2020/09/27/231438)
- [How can I use GeoPandas to read a string containing GeoJSON content into a GeoDataFrame?](https://gis.stackexchange.com/questions/420163/how-can-i-use-geopandas-to-read-a-string-containing-geojson-content-into-a-geoda)
- [geopandasで複数のポリゴンを結合して描画する](https://qiita.com/HidKamiya/items/30c0620ded6013979cad)
- [Make a union of polygons in GeoPandas, or Shapely (into a single geometry)](https://stackoverflow.com/questions/40385782/make-a-union-of-polygons-in-geopandas-or-shapely-into-a-single-geometry)
- [The Shapely User Manual](https://shapely.readthedocs.io/en/stable/manual.html#shapely.ops.unary_union)
- https://stackoverflow.com/questions/73689520/how-to-create-a-charfield-with-suggestions-in-django-forms
- https://stackoverflow.com/questions/24783275/django-form-with-choices-but-also-with-freetext-option/32791625#32791625

## 出典

- [国土地理院ウェブサイト・地理院タイル・標準地図](https://maps.gsi.go.jp/development/ichiran.html#std)