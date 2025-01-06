from typing import List, Tuple, Dict
from collections import defaultdict
import requests
import json


def manhattan_distance(horizontal_dist: Tuple[int, int],
                       vertical_dist: Tuple[int, int]) -> int:
    """
    Calculate Manhattan distance between two points

    Args:
        horizontal_dist (Tuple[int, int]): Coordinates of the horizontal points (x1, x2)
        vertical_dist (Tuple[int, int]): Coordinates of the vertical points (y1, y2)

    Return:
        Integer: Manhattan distance between the two distances
    """
    # Unpack tuples and perform the formula
    x1, x2 = horizontal_dist[0], horizontal_dist[1]
    y1, y2 = vertical_dist[0], vertical_dist[1]
    return abs(x1 - x2) + abs(y1 - y2)


def fetch_rider_and_driver_coords(grid: List[List[int]]) -> Dict[int, Tuple[int, int]]:
    """
    Obtains each riders/driver (x,y) position on a 2D grid

    Args:
        grid (List[List[int]]): A 2D grid representing the location of each driver or rider
            - Grid cells contain integers, where:
                - `-1` indicates no rider
                - Other integers represent rider or driver IDs

    Returns:
        Dict: A dictonary where the rider ID (int) represents the key and
            values are the coordinates of the rider (column, row)

    Example:
        grid = [
              [ 1,-1,-1,-1,-1],
              [-1,-1,-1,-1,-1],
              [-1,-1,-1, 2,-1],
              [-1, 3,-1,-1,-1],
              [-1,-1,-1,-1,-1]
            ]
        fetch_rider_and_driver_coords(grid)

        Output:
        {1: (0, 0), 2: (3, 2), 3: (1, 3)}
    """

    # Find the coordinates of driver/rider
    n = len(grid)
    coords: Dict = {}
    for row in range(n):
        for column in range(n):
            if grid[row][column] != -1:
                coords[grid[row][column]] = column, row
    return coords


def fetch_driver_passengers(requests: List) -> Dict[int, List[int]]:
    """
    Obtain all riders associated with each driver

    Args:
        requests (List): A list of requests where each request is represented as a dictionary containing:
            - `driverId` (int): ID of the driver
            - `riderIds` (List[int]): ID of the list of riders
            - `accepted` (bool): Flag that checks if the driver accepted
                                 the request from the rider

    Returns:
        Dict[int, List[int]]: A dictionary mapping driver IDs to lists of rider IDs associated with them

    Example:
        requests = [
                {"driver": 1, "rider": 5, "accepted": True},
                {"driver": 1, "rider": 6, "accepted": True},
                {"driver": 2, "rider": 7, "accepted": True},
                {"driver": 3, "rider": 9, "accepted": False},
             ]
        fetch_driver_passengers(requests)

        Output:
        {1: [5, 6], 2: [7]}
    """

    driver_passengers: Dict = defaultdict(list)

    # Dictonary for the driver mapped to list of riders
    for request in requests:
        if request["accepted"] is True:
            driver_passengers[request["driver"]] += [request["rider"]]
    return driver_passengers


def create_entry(driver_id: int, rider_ids: List[int],
                 avg_pickup: Dict[int, Tuple[int, int]],
                 avg_dropoff: Dict[int, Tuple[int, int]]) -> Dict:
    """
    Creates a dictonary map of all the values as a statistics

    Args:
        driver_id (int): ID of the driver
        rider_ids (List[int]): List of the riders associated with the driver
        avg_pickup (Dict[int, Tuple[int, int]]): Dictonary, where the driver is the key and value as
                                                the average pickup (x, y)
        avg_dropoff (Dict[int, Tuple[int, int]]): Dictonary, where the driver is the key and value as
                                                the average dropoff (x, y)

    Returns:
        Dictonary containing the statistics of the driver

    Example:
        avg_pickup = {1: (5, 1), 2: (4, 9)}
        avg_dropoff = {1: (0, 0), 2: (7, 6)}

        create_entry(1, [4, 3, 6], avg_pickup, avg_dropoff)

        Output:
        {
             "driverId": 1,
             "riderIds": [4, 3, 6],
             "averagePickup": {"x": 5, "y": 1},
             "averageDropoff": {"x": 0, "y": 0}
        }
    """
    # Checking if average pickup or dropoff is empty
    if avg_pickup:
        pickup_x = avg_pickup[driver_id][0]
        pickup_y = avg_pickup[driver_id][1]
    else:
        pickup_x, pickup_y = None, None

    if avg_dropoff:
        dropoff_x = avg_dropoff[driver_id][0]
        dropoff_y = avg_dropoff[driver_id][1]
    else:
        dropoff_x, dropoff_y = None, None

    # Statistics for each group
    return {
        "driverId": driver_id,
        "riderIds": rider_ids,
        "averagePickup": {"x": pickup_x, "y": pickup_y},
        "averageDropoff": {"x": dropoff_x, "y": dropoff_y}
    }


def calculate_coord_total(pairs: List[Tuple[int, int]]):
    """
    Calculates the total x and y of the coordinates for
    the given list of dropoff/pickup locations

    Args:
        pairs (List[Tuple[int, int]]): The (x, y) coords location of a list of riders

    Return:
        Tuple(int, int, int), where the

        first int - total X coords
        second int - total y coords
        last int - length of all the pairs
    """
    n = len(pairs) + 1  # + 1 to account for the driver

    # Getting the sum of the x & y coords for riders
    x_total = sum(pair_x[0] for pair_x in pairs)
    y_total = sum(pair_y[1] for pair_y in pairs)

    return x_total, y_total, n


def calculate_average_coords(driver_passengers: Dict[int, List[int]],
                             pickup_coords: Dict[int, Tuple[int, int]],
                             dropoff_coords: Dict[int, Tuple[int, int]]) -> \
        Tuple[Dict[int, Tuple[int, int]], Dict[int, Tuple[int, int]]]:
    """
    Calculates the average position of dropoff and pickupoff location

    Args:
        driver_passengers (Dict[int, List[int]]): Dictonary, where the driver is the key and
                                                value is the list of riderIds associated with it
        pickup_coords (Dict[int, Tuple[int, int]]): Dictonary, where the rider is the key and
                                                value is a tuple (x, y) representing the pickup coords
        dropoff_coords (Dict[int, Tuple[int, int]]): Dictonary, where the rider is the key and
                                                value is a tuple (x, y) representing the dropoff coords
    Return:
        Dict, where the key is the driver and value is the average pickup coords of the driver and rider
        Dict, where the key is the driver and value is the average droppoff coords of the driver and rider

    Example:
        driver_passengers = {5: [3, 4]}
        pickup_coords = {3: (12, 13), 4: (2, 9), 5: (13, 7)}
        dropoff_coords = {3: (13, 1), 4: (3, 11), 5: (11, 10)}
        print(calculate_average_coords(5, pickup_coords, dropoff_coords))

        Output:
        ({5: (9,9)}, {5, (9,7)})

    """
    # driverId mapped to avg pickup/dropoff
    avg_pickup_location: Dict[int, Tuple[int, int]] = {}
    avg_dropdown_location: Dict[int, Tuple[int, int]] = {}

    for driver, riders in driver_passengers.items():
        # Check if there is riders
        if riders:
            # Getting the pairs of pickup/dropoff
            pickup_pairs = [pickup_coords[rider] for rider in riders]
            dropoff_pairs = [dropoff_coords[rider] for rider in riders]

            # Getting the total for pickup, and dropoff, and length
            pickup_x, pickup_y, n = calculate_coord_total(pickup_pairs)
            dropoff_x, dropoff_y, n = calculate_coord_total(dropoff_pairs)

            # Checking if pickup_coords is not empty
            if pickup_coords is not None:
                # Accounting for the driver's coords
                pickup_x += pickup_coords[driver][0]
                pickup_y += pickup_coords[driver][1]

            # Checking if dropoff_coords is not empty
            if dropoff_coords is not None:
                # Accounting for the driver's coords
                dropoff_x += dropoff_coords[driver][0]
                dropoff_y += dropoff_coords[driver][1]

            # Getting the average
            avg_pickup_location[driver] = (pickup_x // n,
                                           pickup_y // n)

            avg_dropdown_location[driver] = (dropoff_x // n,
                                             dropoff_y // n)

    return avg_pickup_location, avg_dropdown_location


def fetch_response(url: str):
    """
    GET API data and parse it into a Python Object

    Args:
        url (str): API endpoint for retrieving and submitting data

    Return:
    Dict: A Python dictonary of the data
         - If the data is fetched unsuccesfully then return None
    """

    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data:
            return data
        else:
            print("Unexpected Status Code:", response.status_code)
            return None

    except Exception as error:
        print(f"Error Fetching Data From {url}:", error)
        return None


def post_response(url: str, json_stats_sorted: str):
    """
    POST parsed API data

    Args:
        url (str): API endpoint for retrieving and submitting data
        json_stats_sorted: Sorted statistics using manhattan distance 
                    in ascending order

    Return:
        str: A message that tells you what kind of response was recieved
            - If the request status is 200, then it returns a sucess message
            - If the request status is not 200, then returns a unsucessful message
    """
    # Post the parsed data back to the API endpoint
    response = requests.post(url,
                             data=json_stats_sorted,
                             headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        return f"Succesful: {response.text}"
    else:
        return f"Request Failed Error: {response.text}"


def process_and_post_statistics(url: str):
    """
    Process data from a API endpoint and generate statistics about that data and post it

    This function does the following steps:
    1. GET data from provided API endpoint
    2. Extract driver, passenger, pickupLocations, dropoffLocations information
    3. Calculates average pickup and dropoff locations for each group
    4. Creates statistical entries for each group
    5. Sorts the entries using Manhattan distance formula
    6. POST data back to the API endpoint

    Args:
        url (str): API endpoint for retrieving and submitting data

    Return:
    List[Dict]: Sorted groups of the statistics using manhattan distance formula
        - None, if fetching failed or data is empty
    """

    data = fetch_response(url)

    if data is None:
        return "Fail to GET data"

    # Unsorted statistics for each group
    stats = []

    # Fetching relevant data
    driver_passengers = fetch_driver_passengers(data["requests"])
    pickup_locations = fetch_rider_and_driver_coords(
        data["pickupLocations"])
    dropoff_locations = fetch_rider_and_driver_coords(
        data["dropoffLocations"])
    pickup_avg, dropoff_avg = calculate_average_coords(driver_passengers,
                                                       pickup_locations,
                                                       dropoff_locations)

    # Loop through the driver groups
    for driver, riders in driver_passengers.items():
        stats.append(create_entry(driver, riders, pickup_avg, dropoff_avg))

    # Sort the list of dictonaries in ascending order using manhattan distance
    stats_sorted: List[Dict] = sorted(stats, key=lambda s: manhattan_distance(
        (s["averagePickup"]["x"], s['averageDropoff']["x"]),
        (s['averagePickup']["y"], s['averageDropoff']["y"])))

    # Convert to JSON string and POST it
    json_stats_sorted = json.dumps(stats_sorted, indent=2)
    response = post_response(url, json_stats_sorted)

    print(response)

    return stats_sorted


# process_and_post_statistics("API")
