import unittest
from sources.api.bus import *


class BusApiTestCase(unittest.TestCase):
    def test_something(self):

        stops = load_stop_data("../../dataset/busstpos/kanagawa/P11-22_14.geojson")

        stop_expected = BusStop(
            name="石楯尾神社前",
            group="富士急バス（株）",
            routes=["【上野原】上野原駅〜バイパス〜井戸"],
            geometry=Geometry(
                Type="Point",
                Coordinates=[
                    Coordinate(Lng=139.11941424235914, Lat=35.656690758905484)
                ],
            ),
        )

        self.assertEqual(stop_expected, stops[0])  # add assertion here


if __name__ == "__main__":
    unittest.main()
