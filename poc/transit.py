import re

import bs4.element
import requests
from bs4 import BeautifulSoup


def _analyze_yahoo_transit_route_summary(route_data: bs4.element.PageElement) -> dict:
    time_required_raw = (
        route_data.find("li", class_="time").text
        if route_data.find("li", class_="time") is not None
        else ""
    )
    print(time_required_raw)

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


def main():
    result = requests.get(
        "https://transit.yahoo.co.jp/search/result?from=新宿車庫前&to=東京オペラシティ南&fromgid=&togid=&flatlon=&tlatlon=&via=&viacode=&y=2024&m=12&d=19&hh=12&m1=0&m2=5&type=5&ticket=ic&expkind=1&userpass=1&ws=3&s=1&al=1&shin=1&ex=1&hb=1&lb=1&sr=1",
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        }
    )
    # print(result.text)
    routes = _analyze_yahoo_transit_search_result_html2(result)
    print(routes)

if __name__ == "__main__":
    main()