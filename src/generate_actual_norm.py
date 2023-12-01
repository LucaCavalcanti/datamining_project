from copy import deepcopy
import json
import random
import sys
import numpy as np


"""
==================GLOBAL VARIABLES==================
"""

drivers = int(sys.argv[1])
number_of_cities = int(sys.argv[2])
max_actualroutes_per_driver = int(sys.argv[3])

TRIPS_CHANGED_MIN_MEAN = 0
TRIPS_CHANGED_MAX_MEAN = 100
TRIPS_CHANGED_MIN_VARIANCE = 0
TRIPS_CHANGED_MAX_VARIANCE = 30


"""
==================SETUP==================
"""

def generate_italian_cities():
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

def get_standard():
    with open("data/standard.json") as json_file:
        standard_routes = json.load(json_file)
    return standard_routes

def create_drivers():
    drivers_list = []
    for i in range(drivers):
        drivers_list.append(Driver(i))
    return drivers_list


"""
==================CLASSES==================
"""

class Preferences:
    def __init__(self):
        # preferenza 1 - vettore di pesi per determinare probabilità di ogni azione di modifica
        self.changes_probability = np.random.uniform(0, 1, 3)
        self.changes_probability = self.changes_probability / np.sum(self.changes_probability)

        # preferenza 2 - media e varianza della normale usata per cambiare il numero di trips in una route
        self.number_of_trips_changed = [random.randint(TRIPS_CHANGED_MIN_VARIANCE, TRIPS_CHANGED_MAX_MEAN), 
                                        random.randint(TRIPS_CHANGED_MIN_VARIANCE, TRIPS_CHANGED_MAX_VARIANCE)]

        # preferenza 3 - vettore di pesi per ogni città
        self.cities = np.random.uniform(0, 1, number_of_cities)
        self.cities = self.cities / np.sum(self.cities)

    def get_number_of_trips_to_change(self, route_len):
        # pesca dalla normale:              media                            varianza
        percentage = np.random.normal(self.number_of_trips_changed[0], self.number_of_trips_changed[1])
        percentage = 0 if percentage < 0 else 100 if percentage > 100 else percentage

        # il numero di trip da modificare equivale a route_len * actual percentage 
        return int(route_len * (percentage/100))

    def __str__(self):
        return f"trip change type probability: {self.changes_probability}, trips change percentage: {self.number_of_trips_changed[0]}% +- {self.number_of_trips_changed[1]}%, city weights: {self.cities}"


class Driver:
    def __init__(self, counter):
        self.preferences = Preferences()
        self.id = str("D" + str(counter))

    def __str__(self):
        return f"{self.id}: {self.preferences}"


"""
==================ACTUAL ROUTES GENERATION==================
"""

def change_index(actual_route_copy, driver, cities, index, trips_added, change_type):
    # if the change is to skip, remove the trip from the route
    if change_type == "skip" and len(actual_route_copy) > 1:
        if index + trips_added - 1 >= 0 and index + trips_added + 1 < len(actual_route_copy):
            actual_route_copy[index + trips_added - 1]["to"] = actual_route_copy[index + trips_added + 1]["from"]
        actual_route_copy.pop(index + trips_added)
        trips_added -= 1
        print("removed trip")

    # if the change is to add, add a trip to the route
    elif change_type == "add":
        new_city = cities[np.random.choice(range(number_of_cities), p=driver.preferences.cities)]
        trip = {"from": new_city, "to": actual_route_copy[index + trips_added]["from"], "merchandise": {}}
        if index + trips_added - 1 >= 0:
            actual_route_copy[index + trips_added - 1]["to"] = new_city
        actual_route_copy.insert(index + trips_added, trip)
        trips_added += 1
        print("added trip: ", trip)

    # if the change is to change, change the trip with a random city
    elif change_type == "change":
        new_city = cities[np.random.choice(range(number_of_cities), p=driver.preferences.cities)]
        actual_route_copy[index + trips_added]["from"] = new_city
        if index + trips_added - 1 >= 0:
            actual_route_copy[index + trips_added - 1]["to"] = new_city
        print("changed trip to: ", new_city)
    
    return actual_route_copy, trips_added

def print_actual_route(actual_route):
    # pretty print actual route
    for trip in actual_route:
        print(trip)
    print("\n")

def apply_changes_to_indexes(actual_route, driver, cities, indexes_to_change):
    # create a copy of the actual route to modify
    actual_route_copy = deepcopy(actual_route)

    # keep track of the number of trips added and removed
    trips_added = 0
    print_actual_route(actual_route_copy)

    # for each index to change, sample from the driver's preferences the type of change to apply
    for index in indexes_to_change:
        change_type = np.random.choice(["skip", "add", "change"], p=driver.preferences.changes_probability)
        print("change type: ", change_type, " at index: ", index, ", trips added: ", trips_added, ", index + trips_added: ", index + trips_added)

        actual_route_copy, trips_added = change_index(actual_route_copy, driver, cities, index, trips_added, change_type)

        print_actual_route(actual_route_copy)

    return actual_route_copy

# modify a route following the driver's preferences
def modify_route(actual_route, driver, cities):
    # sample from the normal the percentage of trips to change
    route_len = len(actual_route)
    trips_to_change = driver.preferences.get_number_of_trips_to_change(route_len)
    print("trips to change: ", trips_to_change)

    # get a set of indexes to change by following the trips_to_change percentage
    indexes_to_change = random.sample(range(route_len), trips_to_change)
    indexes_to_change.sort()
    print("indexes to change: ", indexes_to_change)

    actual_route_copy = apply_changes_to_indexes(actual_route, driver, cities, indexes_to_change)

    return actual_route_copy

def generate_actual_routes():
    actual_routes = []

    # create drivers with respective preferences and obtain standard routes and cities to use
    drivers_list = create_drivers()
    standard_routes = get_standard()
    cities = generate_italian_cities()

    counter = 0
    for driver in range(drivers):
        print(drivers_list[driver])

        for k in range(random.randint(1, max_actualroutes_per_driver)):
            actual_route_id = "a" + str(counter)
            # select a random standard route
            actual_route = deepcopy(standard_routes[random.randint(0, len(standard_routes) - 1)])
            print("chosen standard route: ", actual_route["id"])

            modified_actual_route = modify_route(actual_route["route"], drivers_list[driver], cities)
            actual_routes.append({"id": actual_route_id, "driver" : drivers_list[driver].id , "sroute" : actual_route["id"]  , "route": modified_actual_route})
            counter+=1
            print("\n")
        print("====================================")

    return actual_routes


"""
==================MAIN==================
"""

if __name__ == "__main__":  
    """ 
    FUNZIONAMENTO GENERALE
    preferenza driver #1 - probabilità del tipo di modifica
    idea - un vettore di pesi determina con che probabilità il driver esegua una certa azione (cambia città/skippa città/aggiungi città)

    preferenza driver #2 - modifiche alle source/dest delle route
    idea - il valore indica quanto andare a modificare una route (percentuale maybe?)
    ad ogni standard route scelta, il driver pesca una percentuale di modifica da applicare

    preferenza driver #3 - scelta effettiva delle città
    idea - prendendo le città disponibili, assegnare ad ognuna un peso e pescare da questo set quando si vanno a fare delle modifiche

    preferenza driver #4 - modifiche al merchandise
    idea - definire per ogni driver una gaussiana multivariata che determina, per ogni elemento, quanto il driver preferisca aggiungere o togliere 

    preferenza driver #5 - numero di merchandise trasportata?
    idea - da valutare
    """
    actual_routes = generate_actual_routes()
    json_output = json.dumps(actual_routes, indent=4)

    # Print the JSON output
    output = open("data/actual_normal.json", "w")
    output.write(json_output)