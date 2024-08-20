from django.apps import AppConfig

from engine.bus import load_stop_data
from engine.train import load_station_data


class MyAppConfig(AppConfig):
    name = "app"
    verbose_name = "app"

    def ready(self):
        pass
