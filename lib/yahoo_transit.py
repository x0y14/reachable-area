import re
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from lib.busstop import BusStop


def _analyze_yahoo_transit_search_result_html(response: requests.Response) -> list[dict]:
    result = []
    soup = BeautifulSoup(response.content, 'html.parser')
    routes = soup.find_all(class_="routeSummary")
    for route in routes:
        time_required_raw = route.find("li", class_="time").text if route.find("li", class_="time") is not None else ""
        transfer_raw = route.find(class_="transfer").text if route.find(class_="transfer") is not None else ""
        fare_raw = route.find(class_="fare").text if route.find(class_="fare") is not None else ""
        distance_raw = route.find(class_="distance").text if route.find(class_="distance") is not None else ""

        time_required_group = re.findall(r"([0-9]+)分", time_required_raw)
        time_required = int(time_required_group[-1])

        transfer_group = re.findall(r"([0-9])回", transfer_raw)
        transfer = int(transfer_group[-1])

        fare_group = re.findall(r"([0-9]+)円", fare_raw)
        fare = int(fare_group[-1])

        distance_group = re.findall(r"([0-9.]+)km", distance_raw)
        distance = float(distance_group[-1])

        result.append(
            {
                "time_required": time_required,
                "transfer": transfer,
                "fare": fare,
                "distance": distance,
            }
        )

    return result


def get_route_yahoo_transit(from_: BusStop, to: BusStop) -> list[dict]:
    # 必須パラメータのみのサンプルurl
    # https://transit.yahoo.co.jp/search/result?from=厚木バスセンター%2F神奈川中央交通&to=神奈川工科大学%2F神奈川中央交通&y=2024&m=07&d=19&hh=10&m1=3&m2=6&type=5&ticket=ic&expkind=1&userpass=1&ws=3&s=0&al=0&shin=0&ex=0&hb=0&lb=1&sr=0

    url = "https://transit.yahoo.co.jp/search/result"

    # 検索条件パラメータの構成 日本語注釈は要検証
    # 出発、到着のバス駅名
    from_busstop_name = f"{from_.name}/{from_.group.replace('（株）', '')}"
    to_busstop_name = f"{to.name}/{to.group.replace('（株）', '')}"

    # 日時
    now = datetime.now(timezone(timedelta(hours=+9), 'JST'))
    y = now.year
    m = now.month
    d = now.day
    hh = now.hour
    _min = str(now.minute).zfill(2)
    m1 = int(_min[0])
    m2 = int(_min[1])
    type_ = 5  # 出発=1, 到着=2, 始発=3, 終電=4, 指定なし=5

    # 運賃
    exp_kind = 1  # ICカード優先=1, 現金(きっぷ)優先=2
    user_pass = 1  # 自由席優先=1, 指定席優先=2, グリーン車優先=3

    # 条件
    ws = 3  # walk-speed? 急いで=1, 少し急いで=2, 少しゆっくり=3, ゆっくり=4
    s = 0  # show-rule? 到着が早い順=0, 料金が安い順=1, 乗り換え回数順=2

    # 手段
    al = 0  # air-load 空路
    shin = 0  # shinkansen 新幹線
    ex = 0  # express 特急
    hb = 0  # high-speed-bus? 高速バス
    lb = 1  # load?/bus? 路線/連絡バス
    sr = 0  # sea-road フェリー

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    result = requests.get(url=url, headers=headers, params={
        "from": from_busstop_name, "to": to_busstop_name,
        "y": y, "m": m, "d": d, "hh": hh, "m1": m1, "m2": m2, "type": type_,
        "expkind": exp_kind, "userpass": user_pass,
        "ws": ws, "s": s,
        "al": al, "shin": shin, "ex": ex, "hb": hb, "lb": lb, "sr": sr
    })

    return _analyze_yahoo_transit_search_result_html(result)
