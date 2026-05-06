import requests
import pandas as pd

url = "https://services2.arcgis.com/JkPEgZJGxhSjYOo0/arcgis/rest/services/BusService/FeatureServer/3/query"

params = {
    "where": "1=1",
    "outFields": "*",
    "f": "geojson",
    "outSR": "4326",
    "resultRecordCount": 2000,
    "resultOffset": 0,
}

def get_first_coordinate_pair(coords):
    """Return the first [lon, lat] pair from nested GeoJSON coordinates."""
    while isinstance(coords[0], list):
        coords = coords[0]
    return coords

all_rows = []

while True:
    print(f"Downloading records from offset {params['resultOffset']}...")

    response = requests.get(url, params=params)
    data = response.json()

    features = data.get("features", [])

    if not features:
        break

    for feature in features:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        lon_lat = get_first_coordinate_pair(coords)

        props["lon"] = float(lon_lat[0])
        props["lat"] = float(lon_lat[1])

        all_rows.append(props)

    params["resultOffset"] += 2000

stops = pd.DataFrame(all_rows)

stops.to_csv("data/bus_stops.csv", index=False)

print("✅ Saved bus stops to data/bus_stops.csv")
print(stops[["lon", "lat"]].head())
print(stops.shape)