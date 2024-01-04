# every driver take a standard route but he will possibly change it according to his preferences
# we need to create a new json file in which we associate to each driver a standard route and we wrote
# the route that he takes (so we write the changes that he makes to the standard route and the changes that he makes
# in the delivery of the merchandise)
# first of all we take a standard route and we assign it to a driver

import json
import random
import sys
from copy import deepcopy

drivers = int(sys.argv[1])
number_of_cities = int(sys.argv[2])
max_actualroutes_per_driver = int(sys.argv[3])

with open("data/merchandise/merchandise_small.json") as merch_file:
    merchandise_global = json.load(merch_file)

MIN_MERCH = 1
MAX_MERCH = 100

def get_standard():
    with open("data/small2/standard_small.json") as json_file:
        standard_routes = json.load(json_file)
    return standard_routes

def generate_italian_cities(number_of_cities):
    cities_file = open("data/cities/italian_cities.csv", "r")
    cities = []
    cities_file.readline()
    counter = 0
    for cities_file_line in cities_file.readlines():
        if counter == number_of_cities:
            break
        cities.append(cities_file_line.split(";")[5].replace('"',''))
        counter += 1
    return cities

# def print_actual_route(actual_route, position, trip):
#     counter = 0
    # print(actual_route["id"])
    # print("current trip: ", trip["from"], " ", trip["to"])
    # print(actual_route["route"][0]["from"])
#     for trip in actual_route["route"]:
#         if counter == position:
            # print(trip["from"], "<------")
            # print(trip["to"], "<------")
#         else:
            # print(trip["from"])
            # print(trip["to"])
#         counter += 1
    # print("\n")

def generate_actual_routes():
    output = open("data/small2/actual_small.json", "w")
    output.write("[\n")
    routes = []
    standard_routes = get_standard()
    counter = 0
    drivers_dict = {}
    drivers_counters = {}
    for driver in range(drivers):
        #drivers cannot be encoded with single letters, change encoding to D + driver count
        driver_id = str("D" + str(driver))
        drivers_dict[driver_id] = random.randint(1, max_actualroutes_per_driver)
        drivers_counters[driver_id] = 0
    
    for k in range(sum(drivers_dict.values())):
        actual_route_id = "a" + str(counter)
        # pick a random driver
        driver_id = random.choice(list(drivers_dict.keys()))
        # check if the driver has already reached the max number of actual routes
        while drivers_counters[driver_id] >= drivers_dict[driver_id]:
            driver_id = random.choice(list(drivers_dict.keys()))
        drivers_counters[driver_id] += 1
        print(driver_id)
        # select a random standard route
        actual_route = deepcopy(standard_routes[random.randint(0, len(standard_routes) - 1)])
        modified_actual_route = modify_route(actual_route)
        # routes.append({"id": actual_route_id, "driver" : driver_id , "sroute" : actual_route["id"]  , "route": modified_actual_route["route"]})
        # print the route in json format without appending to routes
        json_output = json.dumps({"id": actual_route_id, "driver" : driver_id , "sroute" : actual_route["id"]  , "route": modified_actual_route["route"]}, indent=4)
        output.write(json_output)
        if k < sum(drivers_dict.values())-1:
            output.write(",\n")
        else:
            output.write("\n")

        counter+=1
    output.write("]")
    # return routes

def modify_route(actual_route):
    # modify the standard route according to the driver preferences
    # for each city of the route choose in a random way if keep the city or skip it or change it and with which city
    counter = 0

    # random chance to modify the starting city
    if random.randint(0, 1) == 0:
        if random.randint(0, 1) == 0:
            actual_route["route"][0]["from"] = cities[random.randint(0, len(cities) - 1)]
    for trip in (actual_route["route"]):
        # print("start of for cycle, counter: ", counter)
        # print_actual_route(actual_route, counter, trip)
        if random.randint(0, 1) == 0:
            # change the city or skip it or add it
            if random.randint(0, 1) == 0:
                # change the city
                # print("Changing a city.")
                trip["to"] = cities[random.randint(0, len(cities) - 1)]
                if counter+1 < len(actual_route["route"]):
                    actual_route["route"][counter+1]["from"] = trip["to"]
            else:
                # skip the city
                # print("Skipping a city.")
                if counter+1 < len(actual_route["route"]):
                    trip["to"] = actual_route["route"][counter+1]["to"]
                    # counter+=1
                    del actual_route["route"][counter+1]
        else:
            if random.randint(0, 1) == 0:
                # add the city
                if counter > 0:
                    merchandise = {}
                    for j in range(random.randint(1, len(merchandise_global))):
                        merchandise[random.choice(merchandise_global)] = random.randint(MIN_MERCH, MAX_MERCH)
                    new_trip = {"from": actual_route["route"][counter-1]["to"], "to": cities[random.randint(0, len(cities) - 1)], "merchandise": merchandise}
                    """ print("Adding a new trip.")
                    print("counter: ", counter, "actual_route id", actual_route["id"])
                    print("bug? ", actual_route["route"][counter-2]["to"]) """
                    # new_trip = {"from": actual_route["route"][counter-1]["to"], "to": cities[random.randint(0, len(cities) - 1)]}
                    actual_route["route"].insert(counter, new_trip)
                    if counter+1 < len(actual_route["route"]):
                        actual_route["route"][counter+1]["from"] = new_trip["to"]
                    # counter+=1
        counter+=1
        
        # separate, random chance to modify the merch (50% chance that each )
        merch = trip["merchandise"]
        merch_copy = deepcopy(merch)
        for merch_name in merch:
            # print(merch_name, ": ", merch[merch_name])
            if random.randint(0, 1) == 0:
                merch_copy[merch_name] += (random.randint(MIN_MERCH, MAX_MERCH) * random.randint(-1, 1))
            # print(merch_name, ": ", merch_copy[merch_name])
            if merch_copy[merch_name] > MAX_MERCH:
                # item went above MAX_MERCH, add a new one TODO: this way of adding new items might be a bit biased
                residue = merch_copy[merch_name] - MAX_MERCH
                merch_copy[merch_name] = MAX_MERCH
                new_merch = random.choice(merchandise_global)
                if not new_merch in merch:
                    merch_copy[new_merch] = residue
                    # print("new merch added: ", new_merch, " - ", residue)
            if merch_copy[merch_name] <= 0:
                # item went under 0, delete it
                del merch_copy[merch_name]
            # print("\n")
        trip["merchandise"] = merch_copy

    return actual_route



if __name__ == '__main__':
    cities = generate_italian_cities(number_of_cities)
    generate_actual_routes()
    # routes = generate_actual_routes()

    # json_output = json.dumps(routes, indent=4)

    # # Print the JSON output
    # output = open("data/small/actual_small.json", "w")
    # output.write(json_output)