import json
import pytest
from main import (manhattan_distance, fetch_rider_and_driver_coords,
                  fetch_driver_passengers, create_entry, calculate_coord_total,
                  calculate_average_coords, fetch_response, post_response, process_and_post_statistics)


@pytest.fixture
def data():
    with open("test_data.json", "r") as file:
        data = json.load(file)
    return data


@pytest.fixture
def solution_data_str():
    with open("test_solution.json", "r") as data:
        data = json.load(data)
    return json.dumps(data)


@pytest.fixture
def solution_data_list():
    with open("test_solution.json", "r") as data:
        return json.load(data)


def test_manhattan_distance():
    # Test with positive coords
    assert manhattan_distance((1, 4), (3, 7)) == 7, "Failed positive coords"

    # Test with negative coords
    assert manhattan_distance((-2, 3), (-5, 1)) == 11, "Failed negative coords"

    # Test with positive and negative coords
    assert manhattan_distance(
        (-1, 3), (2, -4)) == 10, "Failed positive/negative coords"


def test_fetch_rider_and_driver_coords(data):
    expected_pickup_coords = {
        1: (2, 0), 9: (9, 1), 8: (3, 2), 6: (13, 2),
        2: (7, 5), 5: (13, 7), 4: (2, 9), 10: (10, 9),
        7: (8, 13), 3: (12, 13)
    }

    expected_dropoff_coords = {
        3: (13, 1), 8: (9, 2), 2: (4, 4),
        7: (2, 6), 6: (13, 7), 10: (5, 9),
        5: (11, 10), 4: (3, 11), 1: (13, 11),
        9: (8, 13)
    }

    # Test with pickupLocations
    assert fetch_rider_and_driver_coords(
        data["pickupLocations"]) == expected_pickup_coords, "Expected pickup coordinates failed"

    # Test with dropoffLocations
    assert fetch_rider_and_driver_coords(
        data["dropoffLocations"]) == expected_dropoff_coords, "Expected dropoff coordinates failed"

    # Test with empty input
    assert fetch_rider_and_driver_coords(
        {}) == {}, "Expected empty input to return empty coordinates"


def test_fetch_driver_passengers(data):

    data_all_rejected = {
        "requests": [
            {"rider": 4, "driver": 1, "accepted": False},
            {"rider": 4, "driver": 6, "accepted": False},
            {"rider": 7, "driver": 1, "accepted": False}
        ]
    }

    expected_driver_passengers = {
        5: [3, 4], 6: [7, 10],
        1: [2, 8, 9]
    }

    # Test sample data of request key
    assert fetch_driver_passengers(
        data["requests"]) == expected_driver_passengers,  "Driver passengers mapping does not match expected values"

    # Test with empty data
    assert fetch_driver_passengers({}) == {}, "Empty Test Failed"

    # Test with driver that has no passengers
    assert fetch_driver_passengers(
        data_all_rejected["requests"]) == {}, "Failed to account for data rejection"


def test_create_entry():
    avg_pickup = {1: (5, 1), 2: (4, 9)}
    avg_dropoff = {1: (0, 0), 2: (7, 6)}

    # Test with basic numbers
    entry = create_entry(1, [4, 3, 6], avg_pickup, avg_dropoff)
    assert entry == {
        "driverId": 1,
        "riderIds": [4, 3, 6],
        "averagePickup": {"x": 5, "y": 1},
        "averageDropoff": {"x": 0, "y": 0}
    }, "Failed basic test"

    # Test without a rider list
    entry = create_entry(2, [], avg_pickup, avg_dropoff)
    assert entry == {
        "driverId": 2,
        "riderIds": [],
        "averagePickup": {"x": 4, "y": 9},
        "averageDropoff": {"x": 7, "y": 6}
    }, "Failed without a riderlist"

    # Test with missing averagePickup
    entry = create_entry(1, [4, 3], {}, avg_dropoff)
    assert entry == {
        "driverId": 1,
        "riderIds": [4, 3],
        "averagePickup": {"x": None, "y": None},
        "averageDropoff": {"x": 0, "y": 0}
    }, "Failed with None in averagePickup"


def test_calculate_coord_total():

    # Test with a single pair
    assert calculate_coord_total([(1, 2)]) == (1, 2, 2), "Single pair failed"

    # Test with a list of pairs
    assert calculate_coord_total([(1, 2), (3, 4), (5, 6)]) == (
        9, 12, 4), "List of pairs failed"

    # Test with no pairs
    assert calculate_coord_total([]) == (0, 0, 1), "No pair test failed"


def test_calculate_average_coords():

    # Test with single driver with multiple riders
    driver_passengers = {5: [3, 4]}
    pickup_coords = {3: (12, 13), 4: (2, 9), 5: (13, 7)}
    dropoff_coords = {3: (13, 1), 4: (3, 11), 5: (11, 10)}
    assert calculate_average_coords(
        driver_passengers, pickup_coords, dropoff_coords) == ({5: (9, 9)}, {5: (9, 7)}), "Failed single driver with multiple drivers"

    # Test with multiple drivers with multiple riders
    driver_passengers = {5: [3, 4], 6: [7, 8]}

    pickup_coords = {3: (12, 13), 4: (2, 9), 7: (4, 6),
                     8: (5, 5), 5: (13, 7), 6: (13, 2)}

    dropoff_coords = {3: (13, 1), 4: (3, 11),
                      7: (8, 9), 8: (9, 8),
                      5: (11, 10), 6: (13, 7)}
    assert calculate_average_coords(
        driver_passengers, pickup_coords, dropoff_coords) == ({5: (9, 9), 6: (7, 4)}, {5: (9, 7), 6: (10, 8)})

    # Test with an empty
    driver_passengers = {}
    pickup_coords = {}
    dropoff_coords = {}
    assert calculate_average_coords(
        driver_passengers, pickup_coords, dropoff_coords) == ({}, {})


def test_fetch_response(requests_mock, data):

    requests_mock.get("http://sandboxcarpooldata.com/data",
                      json=data, status_code=200)

    requests_mock.get("http://sandboxcarpooldata.com/faildata",
                      json=data, status_code=400)

    requests_mock.get("http://sandboxcarpooldata.com/empty",
                      json={}, status_code=200)

    # Test for sucessful GET 200 response
    assert fetch_response(
        "http://sandboxcarpooldata.com/data") == data, "Failed to match JSON data with Expected data"

    # Test for unsucessful GET 400 response
    assert fetch_response(
        "http://sandboxcarpooldata.com/faildata") is None, "Failed to return None"

    # Test for empty GET 200 response
    assert fetch_response(
        "http://sandboxcarpooldata.com/empty") is None, "Failed Empty Test Case"


def test_post_response(requests_mock, solution_data_str):
    requests_mock.post("http://sandboxcarpool.com/post",
                       status_code=200, text="Worked")

    requests_mock.post("http://sandboxcarpool.com/postfail",
                       status_code=400, text="Fail")

    # Test with status code 200 POST request
    assert post_response("http://sandboxcarpool.com/post",
                         solution_data_str) == "Succesful: Worked"

    # Test with failed POST request
    assert post_response("http://sandboxcarpool.com/postfail",
                         solution_data_str) == "Request Failed Error: Fail"


def test_process_and_post_statistics(requests_mock, data, solution_data_str, solution_data_list):

    # First Assert
    requests_mock.get("http://sandboxcarpool.com/data",
                      json=data, status_code=200)
    requests_mock.post("http://sandboxcarpool.com/data",
                       json=solution_data_str)

    # Second Assert
    requests_mock.get("http://sandboxcarpool.com/datafail",
                      json=data, status_code=400)
    requests_mock.post("http://sandboxcarpool.com/datafail",
                       json=solution_data_str)

    # Third Assert
    requests_mock.get("http://sandboxcarpool.com/dataempty",
                      json={}, status_code=200)
    requests_mock.post("http://sandboxcarpool.com/dataempty",
                       json={})

    # Test with using the sample data provided
    assert process_and_post_statistics(
        "http://sandboxcarpool.com/data") == solution_data_list, "Sorted groups stats does not match expected"

    # Test if the data fetching via, therefore short circuiting occurs
    assert process_and_post_statistics(
        "http://sandboxcarpool.com/datafail") == "Fail to GET data"

    # Test if the data fetching via, therefore short circuiting occurs
    assert process_and_post_statistics(
        "http://sandboxcarpool.com/dataempty") == "Fail to GET data"
