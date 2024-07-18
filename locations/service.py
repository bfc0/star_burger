import requests
from django.conf import settings
from geopy.distance import distance
from .models import Location


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


class CoordinateService:
    def __init__(self, addresses: set[str]):
        self.fetch_all_coords(addresses)

    def fetch_all_coords(self, addresses: set[str]):
        locations = Location.objects.filter(address__in=addresses)

        self.coords_cache = {
            loc.address: (loc.longitude, loc.latitude) for loc in locations
        }

        for address in addresses:
            if address not in self.coords_cache:
                coords = fetch_coordinates(
                    settings.YANDEX_KEY, address) or (None, None)

                Location.objects.create(
                    address=address,
                    longitude=coords[0],
                    latitude=coords[1]
                )
                self.coords_cache[address] = coords

        print(self.coords_cache)

    def get_distance(self, addr_from: str, addr_to: str) -> int | None:
        coords_from = self.coords_cache.get(addr_from)
        coords_to = self.coords_cache.get(addr_to)

        if not coords_from or not coords_to:
            return None

        lon_from, lat_from = coords_from
        lon_to, lat_to = coords_to

        if None in (lon_from, lat_from, lon_to, lat_to):
            return None

        try:
            return int(distance((lat_from, lon_from), (lat_to, lon_to)).km)
        except Exception:
            return None
