import argparse
import time
from typing import List, Tuple

import pandas as pd
import requests
from tqdm import tqdm

OSM_NOMINATIM_URL = (
    "https://nominatim.openstreetmap.org/search?q={}&email={}&format=json&countrycodes=pl,de,cz,sk,ua,by,ru"
)
DUMMY_COORDINATES = float("inf"), float("inf")
SLEEP_SECONDS = 0.9

parser = argparse.ArgumentParser(
    description="Fetch location data of train stations from OpenStreetMap"
)
parser.add_argument(
    "stations_file", type=str, help="name of file containing station names"
)
parser.add_argument("output_file", type=str, help="name of output file")
parser.add_argument(
    "--email",
    type=str,
    help="e-mail address for OSM API abuse contact",
    default="220895@student.pwr.edu.pl",
)


def get_valid_train_station_coordinates(places_data: List) -> Tuple[float, float]:
    coordinates = DUMMY_COORDINATES
    for place in places_data:
        # Assume the first place is the best match
        if coordinates == DUMMY_COORDINATES:
            coordinates = (place["lat"], place["lon"])
        # ...unless there is a railway place
        if place["class"] == "railway":
            coordinates = (place["lat"], place["lon"])
            break
    return coordinates


def fetch_stations(names_list: List[str], email: str) -> List[Tuple[float, float]]:
    coordinates_list = []
    for name in tqdm(names_list):
        response = requests.get(OSM_NOMINATIM_URL.format(name, email))
        response_data = response.json()

        coordinates = get_valid_train_station_coordinates(response_data)

        if coordinates == DUMMY_COORDINATES:
            print(f"Coordinates not found for {name}")

        coordinates_list.append(coordinates)
        time.sleep(SLEEP_SECONDS)
    return coordinates_list


if __name__ == "__main__":
    args = parser.parse_args()

    stations_names = pd.read_csv(args.stations_file, header=None, squeeze=True).tolist()
    stations_locations = fetch_stations(stations_names, args.email)

    stations_dataframe = pd.DataFrame(
        [
            (name, lat, lon)
            for name, (lat, lon) in zip(stations_names, stations_locations)
        ]
    )

    columns = ["station", "latitude", "longitude"]
    stations_dataframe.columns = columns
    stations_dataframe.to_csv(args.output_file, index=False)
