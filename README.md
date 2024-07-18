# 卒研

## 概要
TODO


## データ
**使用している各データは、自ら用意したものでない限りignoreしています。**

### バス停
バス停データは[国土数値情報ダウンロードサイト・バス停留所データ](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-P11-v3_0.html)から取得しています。

| ファイル名             | 設置場所                                        | ダウンロード元             |
|-------------------|---------------------------------------------|---------------------|
| P11-22_14.geojson | dataset/busstpos/kanagawa/P11-22_14.geojson | 神奈川（シェープ、geojson形式） |


### 鉄道駅
鉄道駅のデータは[国土数値情報ダウンロードサイト・鉄道データ](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-v2_3.html)から取得しています。

| ファイル名                  | 設置場所                                    | ダウンロード元       |
|------------------------|-----------------------------------------|---------------| 
| N02-20_Station.geojson | dataset/stations/N02-20_Station.geojson | 全国・世界測地系・令和2年 |



## 参考文献
- [foliumの基本的な使い方とオープンデータ活用](https://qiita.com/Kumanuron-1910/items/12ce7aa02922927de2f4)
- [【folium】地図のMarkerの色や形・アイコン・タイルを変える](https://chayarokurokuro.hatenablog.com/entry/2020/09/02/212350)
- [Python+folium+openrouteserviceを使う (経路・時間行列・等時線を例に)](https://zenn.dev/takilog/articles/2be029ccd35972)