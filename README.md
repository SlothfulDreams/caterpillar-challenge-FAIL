# SandBox Caterpillar Challenge

Rebuilding carpool groups from lost data.

## Install Packages

```ssh
pip install -r requirements.txt
```

If that fails (Manually install all with)

```ssh
pip install pytest

pip install requests

pip install requests-mock==1.12.1
```

## Given Information

- `role` is an integer where 0 indicates a rider and 1 indicates a driver.

- `id` is a unique integer key value

- `name` is the name of the user (Can be ignored)

- `averagePickup` and `averageDropOff` represents a coordinate pair (ex. `{x: 5, y: 10}`)

- **Manhattan distance** formula: $|x_1 - x_2| + |y_1 - y_2|$ used to calculate the difference between the `averagePickup` and `averageDropOff`

- Every rider and driver is in one group

- `User` key of the json data probably does not matter as we can tell who is driver and who is a rider via the `request` key (Ignore the `user` key?)

## Example of pickup/dropoff locations representation

```
[
  [ 1,-1,-1,-1,-1],
  [-1,-1,-1,-1,-1],
  [-1,-1,-1, 2,-1],
  [-1, 3,-1,-1,-1],
  [-1,-1,-1,-1,-1]
]
```

#### Array Interperation:

| Y↓ X→ | 0     | 1     | 2   | 3     | 4   |
| ----- | ----- | ----- | --- | ----- | --- |
| **0** | **1** | -1    | -1  | -1    | -1  |
| **1** | -1    | -1    | -1  | -1    | -1  |
| **2** | -1    | -1    | -1  | **2** | -1  |
| **3** | -1    | **3** | -1  | -1    | -1  |
| **4** | -1    | -1    | -1  | -1    | -1  |

#### Examples of locating users with different ID numbers.

| User ID | Coordinates  |
| ------- | ------------ |
| 1       | {x: 0, y: 0} |
| 2       | {x: 3, y: 2} |
| 3       | {x: 1, y: 3} |

## TODO

- Match Id numbers with numbers inside the grid that represents their coordinates

- Sort groups by ascending order by difference between averagePickup and averageDropoff using Manhattan distance formula

- Check if the rider and driver are compatible before making a entry

- Send the data back after parsing making sure that the Content-Type of the request is application/JSON

## Main Code Functional Goals

- Create a dict to map coordinates of pickup/dropoff locations to unique IDs, with the key as the unique ID and coords as the value

- Create a dict to map drivers to riders, with key as driverId and value as a list of riders associated with the group

- A function that helps find the (x, y) in the grid of pickupLocations and dropoffLocations

- Fetch data from API endpoint and parse it and POST it back

  - The data will be sorted using Manhattan distance formula in ascending order

- Create helper functions to assist with these main goals to reduce a overall complexity of one singular function

- Make a "template" function for each data entry as the format for the parsed data suppose to look like a dictonary for each group
  - Can use this as a helper function

```json
[
  {
    "driverId": 5,
    "riderIds": [
      3,
      4
    ],
    "averagePickup": {
      "x": 9,
      "y": 9
    },
    "averageDropoff": {
      "x": 9,
      "y": 7
    }
]
```

---

# Design Decisions

Before starting to write any line of code. I started basically writing the "documentation" first.

I essentially outlined everything I needed to accomplish before writting the code. Coming up with the core functionalities needed to complete the given task.

Majority of what I wrote above was things I identitfied before writing any line of code.

The [TODO](#todo) served as a entire general overview function

The [Main Code Functional Goals](#main-code-functional-goals) purpose was to be the TODO however more specific on the technical details

### Main Data Structure (HashMap)

- I choose to use a HashMap for the majority of the mapping for driver and riders groups

  - Driver are map to a list of riders assoicated with them

  - Driver's are also mapped to the average pickup and dropoff (Used for the group data)

  - Riders and drivers are both mapped to their coordinates on the grid of pickupLocations and dropoffLocations

- The HashMap allows me to find all relevant data assoicated with the drivers and rider making it extremely easy to use

- Since a HashMap has a O(1) look up and a insert time it makes it very efficent

### Helper Functions

- I made mutiple helper functions to keep the code organized and easy to read.

  - When someone else looks at my code they can see what each little function does instead looking at one big function

  - It also makes it easier for **Unit Testing**
    - Allows you to identifiy what function is wrong faster and potential edge cases of that function

### Unit Testing

I Unit Tested each function using `Pytest` as its simpler and easier to use than the builtin `unittest` library.

- Unit Testing allowed me identitfy potential edge cases
  - It actaully helps me think of the edge cases themselves.
  - I appoarch it like how I would in Fundies 1; I have to think about what kind of tests to write

I also mocked test apis with `request-mock`

- This allows me to test if my methods are working without directly spamming the endpoint API
- If the endpoint API was down I would still be able to test my code

---

# How to Unit Test

Make sure you are in the correct directory on your terminal

Have Pytest and mock-request installed

run

```ssh
pytest
```

---

### Challenges

- Struggled with calculating the averagePickup/Dropoff coordinates
  - I misinterpreted the wording in the prompt.
  - I thought only riders were included in the in calculating the averagePickup ahnd averageDropoff
  - Resolved it via testing different methods of calculation (alot of playing and testing around on paper)
  - I should have figured this out faster but I was too fixated on my calculations being wrong instead of looking at the broader picture

### Key Take Aways

- Learned about generator expressions
- Learned how to document Python code using Google Style
- Learned about how to use Pytest and fixtures
- Learned how to use request-mock
- To not be too fixated on one exact method
  - Was stuck on implementing mock requests using the unittest.mock library

---

# Result (Fail)

## Feedback

- Include a line in the README to point to the entry point (Lots of functions make it confusing to know where it was at)

- Some of the functions could have been abstracted more
  - Calculating the average could have been abstracted more as there was alot of repeated code there
