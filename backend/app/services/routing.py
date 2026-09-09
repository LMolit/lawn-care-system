import httpx

from app.core.config import settings


def get_distance_matrix(locations: list[tuple[float, float]]) -> list[list[float]]:
    """
    locations: list of (latitude, longitude) tuples, start location first.
    Returns a 2D matrix of driving times in seconds between every pair.
    """
    coordinates = [[lng, lat] for lat, lng in locations]

    response = httpx.post(
        "https://api.openrouteservice.org/v2/matrix/driving-car",
        headers={"Authorization": settings.openrouteservice_api_key},
        json={"locations": coordinates, "metrics": ["duration"]},
    )
    response.raise_for_status()
    data = response.json()
    return data["durations"]

def nearest_neighbor_route(
    start_location: tuple[float, float],
    stops: list[dict],
    distance_matrix: list[list[float]],
) -> list[dict]:
    """
    Returns `stops` reordered by nearest-neighbor heuristic.
    distance_matrix[i][j] = travel time from stop i to stop j (index 0 = start_location).
    """
    unvisited = list(range(len(stops)))
    current_index = 0
    ordered_stops = []

    while unvisited:
        nearest = min(unvisited, key=lambda i: distance_matrix[current_index][i + 1])
        ordered_stops.append(stops[nearest])
        unvisited.remove(nearest)
        current_index = nearest + 1

    return ordered_stops
