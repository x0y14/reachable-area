import os.path
import re

import bs4
import requests
from datetime import datetime, timedelta, timezone

from bs4 import BeautifulSoup


import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from definitions import PROJECT_ENGINE_DIR
from .database import get_conn, get_routes, GetRoutesReq, InsertRouteReq, insert_route
from .station import Station
from .transit_type import TransitType
from .utils import list_include

def _analyze_yahoo_transit_route_summary(route_data: bs4.element.PageElement) -> dict:
    time_required_raw = (
        route_data.find("li", class_="time").text
        if route_data.find("li", class_="time") is not None
        else ""
    )
    transfer_raw = (
        route_data.find(class_="transfer").text
        if route_data.find(class_="transfer") is not None
        else ""
    )
    fare_raw = (
        route_data.find(class_="fare").text
        if route_data.find(class_="fare") is not None
        else ""
    )
    distance_raw = (
        route_data.find(class_="distance").text
        if route_data.find(class_="distance") is not None
        else ""
    )
    time_required = ""
    if "乗車" in time_required_raw:
        time_required_group = re.findall(r"乗車([0-9]+)分", time_required_raw)
        if len(time_required_group) != 0:
            time_required = int(time_required_group[-1])
    if time_required == "":
        if "時間" in time_required_raw:
            time_required_group = re.findall(r"([0-9]+)時間([0-9]+)分", time_required_raw)
            h = time_required_group[-1][0]
            m = time_required_group[-1][1]
            time_required = int(h)*60 + int(m)
        else:
            time_required_group = re.findall(r"([0-9]+)分", time_required_raw)
            time_required = int(time_required_group[-1])

    transfer_group = re.findall(r"([0-9])回", transfer_raw)
    transfer = int(transfer_group[-1])

    fare_group = re.findall(r"([0-9]+)円", fare_raw)
    fare = int(fare_group[-1])

    distance_group = re.findall(r"([0-9.]+)km", distance_raw)
    distance = float(distance_group[-1])
    route_summary = {
        "time_required": time_required,
        "transfer": transfer,
        "fare": fare,
        "distance_km": distance,
    }
    return route_summary

def _analyze_yahoo_transit_route_detail_is_include_walk(route_data: bs4.element.PageElement) -> bool:
    detail = route_data.find(class_="routeDetail")
    walks = detail.find_all("div", class_="access walk")
    if len(walks) == 0:
        return False
    return True

def _analyze_yahoo_transit_search_result_html2(
        response: requests.Response,
) -> list[dict]:
    result = []
    soup = BeautifulSoup(response.content, "html.parser")
    search_result = soup.find("div", class_="mdSearchResult")
    if search_result is None:
        return []
    routes = search_result.find(id="srline", class_="elmRouteDetail")
    route_datas = routes.find_all(id=re.compile('^route[0-9]+'))
    for route_data in route_datas:
        # print(route_data)
        route_summary = _analyze_yahoo_transit_route_summary(route_data)
        # print(route_summary)
        is_include_walk = _analyze_yahoo_transit_route_detail_is_include_walk(route_data)
        # print(is_include_walk)
        if is_include_walk is False:
            result.append(route_summary)

    return result


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
        if "乗車" in time_required_raw:
            time_required_group = re.findall(r"乗車([0-9]+)分", time_required_raw)
            time_required = int(time_required_group[-1])
        elif "時間" in time_required_raw:
            time_required_group = re.findall(r"([0-9]+)時間([0-9]+)分", time_required_raw)
            h = time_required_group[-1][0]
            m = time_required_group[-1][1]
            time_required = int(h)*60 + int(m)
        else:
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
                "distance_km": distance,
            }
        )

    return result


def get_route_yahoo_transit(
        transit_type: TransitType,
        from_: Station,
        to: Station,
) -> list[dict]:

    is_bus = True
    if transit_type == TransitType.TRAIN:
        is_bus = False

    # 既にデータあったらそれ返しちゃう
    conn = get_conn(os.path.join(PROJECT_ENGINE_DIR, "cache.db"))
    get_req = GetRoutesReq(
        is_bus_route=is_bus,
        from_=from_,
        to_=to
    )
    routes = get_routes(conn, get_req)
    if len(routes) != 0:
        conn.close()
        return routes
    print(f"cache not found!!: isBus: {get_req.is_bus_route == 1}, {get_req.from_.name}->{get_req.to_.name}")
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
    lb = 0
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

    routes = _analyze_yahoo_transit_search_result_html2(result)
    # 通れないということなので無効だと明確に示す
    if len(routes) == 0:
        insert_req = InsertRouteReq(
            is_bus_route=is_bus,
            from_=from_,to_=to,
            time_required=-1,
            transfer=-1,
            fare=-1,
            distance=-1
        )
        inserted_route = insert_route(conn, insert_req)
        conn.close()
        return [inserted_route]

    for route in routes:
        insert_req = InsertRouteReq(
            is_bus_route=is_bus,
            from_=from_,to_=to,
            time_required=route["time_required"],
            transfer=route["transfer"],
            fare=route["fare"],
            distance=route["distance_km"]
        )

        try:
            print("try insert")
            _ = insert_route(conn, insert_req)
        except Exception as e:
            print("!! insert ERROR !!")
            print(e)
            print(insert_req)

    conn.close()
    return routes



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
        for candidate in ref_station_dict_[TransitType.BUS]:
            if ((set(candidate.management_groups) & set(station.management_groups))
                    and (list_include(station.line_routes, candidate.line_routes))
                    and (candidate.name != station.name)):
                same_line_stations.append(candidate)
    elif station.transit_type == TransitType.TRAIN:
        # for stat in ref_station_dict_[TransitType.TRAIN]:
        #     if (stat.line_routes == station.line_routes) and (stat.name != station.name):
        #         same_line_stations.append(stat)
        for candidate in ref_station_dict_[TransitType.TRAIN]:
            if ((set(candidate.management_groups) & set(station.management_groups))
                    and (list_include(station.line_routes, candidate.line_routes))
                    and (candidate.name != station.name)):
                same_line_stations.append(candidate)
    return same_line_stations

def get_same_line_or_route_stations_with_time(
        from_:Station,
        ref_stations:dict[TransitType, list[Station]],
        limit_min: int) -> list[tuple[int, Station]]:
    result: list[tuple[int, Station]] = []
    # start_time = datetime.now()
    same_line_stations = get_same_line_or_route_stations(from_, ref_stations)
    # end_time = datetime.now()
    # print(f"(1) get_same_line_or_route_stations_with_time: {end_time-start_time}s")
    transit_type = from_.transit_type

    # start_time = datetime.now()
    for same_line_station in same_line_stations:
        will_add = False # 同じ路線かつ到達できる駅として一覧に追加すべきですか?
        min_time_required = 0
        routes = get_route_yahoo_transit(transit_type, from_, same_line_station)
        # routeをすべてチェック
        for route in routes:
            # もし辿り着けない駅だと分かったら
            if route["time_required"] == -1:
                continue
            if (route["transfer"] == 0) and route["time_required"] <= limit_min:
                will_add = True
            # 最低所要時間を更新する
            if min_time_required == 0:
                min_time_required = route["time_required"]
            else:
                if route["time_required"] < min_time_required:
                    min_time_required = route["time_required"]
        if will_add and min_time_required >= 0:
            print(same_line_station.name, min_time_required)
            result.append((min_time_required, same_line_station))
    # end_time = datetime.now()
    # print(f"(2) get_same_line_or_route_stations_with_time: {end_time-start_time}s")

    return result