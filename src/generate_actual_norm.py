# we want to define for each driver a mean and a standard deviation in order to choose
# which cities to modify and how much merchandise to add

from copy import deepcopy
import json
import random
import sys

import numpy as np

drivers = int(sys.argv[1])
number_of_cities = int(sys.argv[2])


def get_standard():
    with open("data/standard.json") as json_file:
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

def generate_actual_routes(mean_driver, standard_deviation_driver):
    routes = []
    standard_routes = get_standard()
    for driver in drivers:
        driver_name = chr(ord("A") + driver)
        actual_route_id = "a" + str(driver)
        actual_route = deepcopy(standard_routes[random.randint(0, len(standard_routes) - 1)])
        modified_actual_route = modify_route(actual_route, mean_driver, standard_deviation_driver, driver)

def generate_random_change(mean, standard_deviation):
    return np.random.normal(mean, standard_deviation)

def modify_route(actual_route, mean_drivers, standard_deviation_drivers, driver_index):
    # modify the standard route according to the driver preferences
    #counter = 0
    for trip in actual_route:
        mean_driver, standard_deviation_driver = get_driver_preferences(mean_drivers, standard_deviation_drivers, driver_index)

        city_change = int(generate_random_change(mean_driver, standard_deviation_driver))

        trip["from"] = city_change + trip["from"]
        trip["to"] = city_change + trip["to"]

        modified_merchandise = {}
        




def create_drivers_preferences():
    mean_driver = []
    standard_deviation_driver = []
    for _ in drivers:
        mean_driver.append(random.randint(0, 100))
        standard_deviation_driver.append(random.randint(0, 100))
    return mean_driver, standard_deviation_driver

def get_driver_preferences(mean_driver, standard_deviation_driver, index):
    return mean_driver[index], standard_deviation_driver[index]


if __name__ == "__main__":
    mean_driver, standard_deviation_driver = create_drivers_preferences()
    generate_actual_routes()