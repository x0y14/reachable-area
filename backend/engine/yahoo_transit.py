import re
import requests
from datetime import datetime, timedelta, timezone

from attr.validators import min_len
from bs4 import BeautifulSoup

from .station import Station
from .transit_type import TransitType
from .utils import list_include


def _analyze_yahoo_transit_search_result_html(
        response: requests.Response,
) -> list[dict]:
    result = []
    soup = BeautifulSoup(response.content, "html.parser")
    routes = soup.find_all(class_="routeSummary")
    for route in routes:
        time_required_raw = (
            route.find("li", class_="time").text
            if route.find("li", class_="time") is not None
            else ""
        )
        transfer_raw = (
            route.find(class_="transfer").text
            if route.find(class_="transfer") is not None
            else ""
        )
        fare_raw = (
            route.find(class_="fare").text
            if route.find(class_="fare") is not None
            else ""
        )
        distance_raw = (
            route.find(class_="distance").text
            if route.find(class_="distance") is not None
            else ""
        )

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


def get_route_yahoo_transit(
        transit_type: TransitType,
        from_: Station,
        to: Station,
) -> list[dict]:
    # 必須パラメータのみのサンプルurl
    # https://transit.yahoo.co.jp/search/result?from=厚木バスセンター%2F神奈川中央交通&to=神奈川工科大学%2F神奈川中央交通&y=2024&m=07&d=19&hh=10&m1=3&m2=6&type=5&ticket=ic&expkind=1&userpass=1&ws=3&s=0&al=0&shin=0&ex=0&hb=0&lb=1&sr=0

    url = "https://transit.yahoo.co.jp/search/result"

    # 検索条件パラメータの構成 日本語注釈は要検証
    # 日時
    now = datetime.now(timezone(timedelta(hours=+9), "JST"))
    y = now.year
    m = str(now.month).zfill(2)
    d = str(now.day).zfill(2)
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

    # 手段, すべて0だったら電車
    al = 0  # air-load 空路
    shin = 0  # shinkansen 新幹線
    ex = 0  # express 特急
    hb = 0  # high-speed-bus? 高速バス
    if transit_type == TransitType.TRAIN:
        lb = 0  # load?/bus? 路線/連絡バス
    elif transit_type == TransitType.BUS:
        lb = 1
    sr = 0  # sea-road フェリー

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    result = requests.get(
        url=url,
        headers=headers,
        params={
            "from": from_.to_yahoo_transit(),
            "to": to.to_yahoo_transit(),
            "y": y,
            "m": m,
            "d": d,
            "hh": hh,
            "m1": m1,
            "m2": m2,
            "type": type_,
            "expkind": exp_kind,
            "userpass": user_pass,
            "ws": ws,
            "s": s,
            "al": al,
            "shin": shin,
            "ex": ex,
            "hb": hb,
            "lb": lb,
            "sr": sr,
        },
    )
    # print(url)
    # print(result.url)

    return _analyze_yahoo_transit_search_result_html(result)


def _transfer_less_than_or_equal(routes: list[dict], transfer_count: int) -> list[dict]:
    result = []
    for route in routes:
        if route["transfer"] <= transfer_count:
            result.append(route)
    return result


def is_able_to_reach_from_either(
        st1: Station, st2: Station, transfer_limit_lq: int
) -> bool:
    # is able to reach from bs1 to bs2?
    route_details = get_route_yahoo_transit(from_=st1, to=st2)
    zt_route_details = _transfer_less_than_or_equal(route_details, transfer_limit_lq)
    if len(zt_route_details) == 0:
        # bs1からbs2に、乗り換えtransfer_limit_lq回で辿り着けない
        return False

    # is able to reach from bs2 to bs1?
    route_details = get_route_yahoo_transit(from_=st2, to=st1)
    zt_route_details = _transfer_less_than_or_equal(route_details, transfer_limit_lq)
    if len(zt_route_details) == 0:
        # bs2からbs1に、乗り換えtransfer_limit_lq回で辿り着けない
        return False

    # you can
    return True


def get_same_line_or_route_stations(
        station: Station,
        ref_station_dict_: dict[TransitType, list[Station]]) -> list[Station]:
    same_line_stations: list[Station] = []

    if station.transit_type == TransitType.BUS:
        for stop in ref_station_dict_[TransitType.BUS]:
            if ((stop.management_groups == station.management_groups)
                    and (list_include(station.line_routes, stop.line_routes))
                    and (stop.name != station.name)):
                same_line_stations.append(stop)
    elif station.transit_type == TransitType.TRAIN:
        for stat in ref_station_dict_[TransitType.TRAIN]:
            if (stat.line_routes == station.line_routes) and (stat.name != station.name):
                same_line_stations.append(stat)
    return same_line_stations

def get_stations_with_time(
        from_:Station,
        ref_stations:dict[TransitType, list[Station]],
        limit_min: int) -> list[tuple[int, Station]]:
    result: list[tuple[int, Station]] = []
    same_line_stations = get_same_line_or_route_stations(from_, ref_stations)
    transit_type = from_.transit_type

    for same_line_station in same_line_stations:
        will_add = False
        min_time_required = -1
        routes = get_route_yahoo_transit(transit_type, from_, same_line_station)
        # routeをすべてチェック
        for route in routes:
            if (route["transfer"] == 0) and route["time_required"] <= limit_min:
                will_add = True
            # 最低所要時間を更新する
            if min_time_required == -1:
                min_time_required = route["time_required"]
            else:
                if route["time_required"] < min_time_required:
                    min_time_required = route["time_required"]
        if will_add:
            result.append((min_time_required, same_line_station))

    return result