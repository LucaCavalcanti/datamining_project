# we want to define for each driver a mean and a standard deviation in order to choose
# which cities to modify and how much merchandise to add

from copy import deepcopy
import json
import random
import sys

import numpy as np

number_of_cities = int(sys.argv[1])


def get_standard():
    '''get the standard routes'''
    with open("data/standard3.json") as json_file:
        standard_routes = json.load(json_file)
    return standard_routes

def get_drivers():
    '''get the list of preferences for each driver'''
    with open("data/drivers.json", "r") as json_file:
        drivers = json.load(json_file)
    return drivers

def generate_italian_cities(number_of_cities):
    '''get the list of italian cities'''
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

def generate_actual_routes(drivers):
    routes = []
    standard_routes = get_standard()
    for driver in drivers:
        id_driver = driver["driver"]
        id_actual_route = f"a{id_driver[1:]}"
        actual_route = deepcopy(standard_routes[random.randint(0, len(standard_routes) - 1)])
        modified_actual_route = modify_route(actual_route['route'], driver)
        routes.append({"id": id_actual_route, "driver": id_driver, "sroute": actual_route["id"], "route": modified_actual_route})
    return routes

def modify_route(actual_route, driver):
    '''modify the standard route according to the preferences of the driver'''
    counter = 0
    for trip in actual_route:
        skip_probability = random.randint(0, 100)
        percentage = get_driver_preference(driver, driver["driver"], trip["from"])
        if skip_probability > percentage:
            # at this point we can choose if skip the city or replace it with another
            # maybe in the future add a percentage that decide if the driver prefer to skip or replace a city
            if random.randint(0, 1):
                # replace it
                for data_city in (driver['preferences']):
                    city = data_city['city']
                    if random.randint(0, 100) <= data_city['percentage']:
                        trip['to'] = city
                        if counter+1 < len(actual_route):
                            actual_route[counter+1]["from"] = trip["to"]
            else:
                # skip it
                if counter+1 < len(actual_route):
                    trip["to"] = actual_route[counter+1]["to"]
                    del actual_route[counter+1]
        counter += 1
    return actual_route

def get_driver_preference(driver, driver_id, city):
    for city_data in driver["preferences"]:
        if city_data['city'] == city:
            return city_data['percentage']
    return []

if __name__ == "__main__":
    drivers = get_drivers()
    if isinstance(drivers, list):
        num_drivers = len(drivers)
    
    routes = generate_actual_routes(drivers)

    json_output = json.dumps(routes, indent=4)

    # Print the JSON output
    output = open("data/actual_preference.json", "w")
    output.write(json_output)