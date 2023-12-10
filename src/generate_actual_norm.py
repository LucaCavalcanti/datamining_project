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

# the variance is the square of the standard deviation. In a normal distribution, variance = 1000 will lead to:
"""
    About 68% of the values would fall between -31.62 and 31.62.
    About 95% of the values would fall between -63.24 and 63.24 (approximately 2 times the standard deviation).
    About 99.7% of the values would fall between -94.86 and 94.86 (approximately 3 times the standard deviation), assuming a normal distribution.
"""
MERCH_CHANGED_MIN_VARIANCE = 0
MERCH_CHANGED_MAX_VARIANCE = 1000

TRIPS_FOR_MERCH_CHANGED_MIN_VARIANCE = 0
TRIPS_FOR_MERCH_CHANGED_MAX_MEAN     = 100
TRIPS_FOR_MERCH_CHANGED_MIN_VARIANCE = 0
TRIPS_FOR_MERCH_CHANGED_MAX_VARIANCE = 80

MIN_MERCH = 1
MAX_MERCH = 100


merchandise = ["milk", "butter", "pens", "tomatoes", "honey", "bread", "pasta", "spaghetti", "pizza", "cookies", "salad", "tortel", 
         "coca-cola", "water", "sparkling water", "orange juice", "arancini", "fanta", "beer", "computer", "phone", "car",
         "train", "sweater", "egg", "carrot", "rice", "soup" , "t-shirt", "jeans", "eyeglasses", "sugar", "salt", "pepper",
         "oil", "rosemary", "thime", "curry", "pepper", "gloves", "spoon", "fork", "knife", "pot", "pan", "wine", "grappa" 
        ]


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

        # preferenza 4 - gaussiana multivariata per il merchandise
        means = np.zeros(len(merchandise))
        covariance_diagonal = np.zeros((len(merchandise), len(merchandise)))
        covariance = np.random.uniform(MERCH_CHANGED_MIN_VARIANCE, MERCH_CHANGED_MAX_VARIANCE, len(merchandise))
        covariance_diagonal = np.diag(covariance)
        self.merchandise_multivariate = [means, covariance_diagonal]

        # preferenza 5 - se il driver vuole aggiungere, togliere, modificare o non fare nulla sulla merchandise
        self.merch_changes_probability = np.random.uniform(0, 1, 4)
        # lower a lot the probability to add merch
        self.merch_changes_probability[0] = self.merch_changes_probability[0] / 10
        self.merch_changes_probability = self.merch_changes_probability / np.sum(self.merch_changes_probability)

        self.number_of_trips_changed_for_merch = [random.randint(TRIPS_FOR_MERCH_CHANGED_MIN_VARIANCE, TRIPS_FOR_MERCH_CHANGED_MAX_MEAN), 
                                        random.randint(TRIPS_FOR_MERCH_CHANGED_MIN_VARIANCE, TRIPS_FOR_MERCH_CHANGED_MAX_VARIANCE)]

    def get_number_of_trips_to_change(self, route_len):
        # pesca dalla normale:              media                            varianza
        percentage = np.random.normal(self.number_of_trips_changed[0], self.number_of_trips_changed[1])
        percentage = 0 if percentage < 0 else 100 if percentage > 100 else percentage

        # il numero di trip da modificare equivale a route_len * actual percentage 
        return int(route_len * (percentage/100))

    def get_number_of_trips_to_change_merch(self, route_len):
        # pesca dalla normale:              media                                       varianza
        percentage = np.random.normal(self.number_of_trips_changed_for_merch[0], self.number_of_trips_changed_for_merch[1])
        percentage = 0 if percentage < 0 else 100 if percentage > 100 else percentage

        # il numero di trip da modificare equivale a route_len * actual percentage 
        return int(route_len * (percentage/100))
    
    def get_percentage_of_merchandise_to_change(self):
        # pesca dalla normale multivariata
        percentage = np.random.multivariate_normal(self.merchandise_multivariate[0], self.merchandise_multivariate[1])
        # print(percentage)
        return percentage

    def __str__(self):
        return f"trip change type probabilities: {self.changes_probability}, trips change percentage: {self.number_of_trips_changed[0]}% +- {self.number_of_trips_changed[1]}%, city weights: {self.cities} \
                merchandise change variance: {self.merchandise_multivariate[1]}, merch trips change probabilities: {self.merch_changes_probability}, \
                merch trips change percentage: {self.number_of_trips_changed_for_merch[0]}% +- {self.number_of_trips_changed_for_merch[1]}%"


class Driver:
    def __init__(self, counter):
        self.preferences = Preferences()
        self.id = str("D" + str(counter))

    def __str__(self):
        return f"{self.id}: {self.preferences}"


"""
==================MODIFY TRIPS==================
"""

def generate_merchandise():
    trip_merchandise = {}
    for j in range(random.randint(1, len(merchandise)-1)):
        trip_merchandise[random.choice(merchandise)] = random.randint(MIN_MERCH, MAX_MERCH)
    return trip_merchandise

def change_index(actual_route_copy, driver, cities, index, trips_added, change_type):
    
    is_last_index = False
    if index + trips_added == len(actual_route_copy):
        is_last_index = True
        print("last index.")

    # if the change is to skip, remove the trip from the route
    if change_type == "skip" and len(actual_route_copy) > 1:
        if index + trips_added - 1 >= 0 and index + trips_added + 1 < len(actual_route_copy):
            actual_route_copy[index + trips_added - 1]["to"] = actual_route_copy[index + trips_added + 1]["from"]
        if is_last_index:
            index -= 1
        actual_route_copy.pop(index + trips_added)
        trips_added -= 1
        print("removed trip")

    # if the change is to add, add a trip to the route
    elif change_type == "add":
        new_city = cities[np.random.choice(range(number_of_cities), p=driver.preferences.cities)]
        if not is_last_index:
            trip = {"from": new_city, "to": actual_route_copy[index + trips_added]["from"], "merchandise": generate_merchandise()}
        else:
            new_city_last = cities[np.random.choice(range(number_of_cities), p=driver.preferences.cities)]
            trip = {"from": new_city, "to": new_city_last, "merchandise": {}}
        if index + trips_added - 1 >= 0:
            actual_route_copy[index + trips_added - 1]["to"] = new_city
        actual_route_copy.insert(index + trips_added, trip)
        trips_added += 1
        print("added trip: ", trip)

    # if the change is to change, change the trip with a random city
    elif change_type == "change":
        new_city = cities[np.random.choice(range(number_of_cities), p=driver.preferences.cities)]
        if not is_last_index:
            actual_route_copy[index + trips_added]["from"] = new_city
            if index + trips_added - 1 >= 0:
                actual_route_copy[index + trips_added - 1]["to"] = new_city
        else:
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
    indexes_to_change = random.sample(range(route_len+1), trips_to_change)
    indexes_to_change.sort()
    print("indexes to change: ", indexes_to_change)

    actual_route_copy = apply_changes_to_indexes(actual_route, driver, cities, indexes_to_change)

    return actual_route_copy


"""
==================MODIFY MERCH==================
"""

def change_merch_at_index(trip_merchandise, driver):
    # generate one merchandise percentage change for all merch in this trip
    percentage = driver.preferences.get_percentage_of_merchandise_to_change()
    
    for merch in merchandise:
        change_type = np.random.choice(["add", "remove", "change", "do_nothing"], p=driver.preferences.merch_changes_probability)

        if change_type == "add" and (merch not in trip_merchandise):
            trip_merchandise[merch] = random.randint(MIN_MERCH, MAX_MERCH)
        if change_type == "remove" and (merch in trip_merchandise) and (len(trip_merchandise) > 1):
            del(trip_merchandise[merch])
        if change_type == "change" and (merch in trip_merchandise):
            print("percentage change: ", percentage[merchandise.index(merch)], " merch before: ", trip_merchandise[merch], " merch change: ", trip_merchandise[merch] * (percentage[merchandise.index(merch)] / 100))
            trip_merchandise[merch] = int(trip_merchandise[merch] + trip_merchandise[merch] * (percentage[merchandise.index(merch)] / 100))
            print("merch after: ", trip_merchandise[merch])
            if trip_merchandise[merch] <= 0:
                # merch went under or is 0, delete it
                del(trip_merchandise[merch])

    return trip_merchandise

def apply_changes_to_trips_merch(actual_route, driver, indexes_to_change):
    # create a copy of the actual route to modify
    actual_route_copy = deepcopy(actual_route)

    print_actual_route(actual_route_copy)

    # for each index to change, sample from the driver's preferences the type of change to apply
    for index in indexes_to_change:
        print("changing merch for trip ", index, ". Merch before: ", actual_route_copy[index]["merchandise"])
        actual_route_copy[index]["merchandise"] = change_merch_at_index(actual_route_copy[index]["merchandise"], driver)

        print("merch after: ", actual_route_copy[index]["merchandise"])
        print("\n\n")

    return actual_route_copy

def modify_merch(actual_route, driver):
    # sample from the normal the percentage of trips where we want to change the merch
    route_len = len(actual_route)
    trips_to_change_merch = driver.preferences.get_number_of_trips_to_change_merch(route_len)
    print("trips where to change merch: ", trips_to_change_merch)

    # get a set of indexes to change by following the trips_to_change_merch percentage
    indexes_to_change = random.sample(range(route_len), trips_to_change_merch)
    indexes_to_change.sort()
    print("indexes to change merch: ", indexes_to_change)

    actual_route_copy = apply_changes_to_trips_merch(actual_route, driver, indexes_to_change)

    print_actual_route(actual_route_copy)

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

            print("changing merch")
            modified_actual_route = modify_merch(actual_route["route"], drivers_list[driver])
            print("changing trips")
            modified_actual_route = modify_route(modified_actual_route, drivers_list[driver], cities)
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
    TODO: qui c'è un problema, ossia il driver non andrà ad allungare di molto il percorso oltre il suo punto di fine, visto che si modificano gli indici. Secondo me va bene così, ma forse vale la pena discuterne

    preferenza driver #3 - scelta effettiva delle città
    idea - prendendo le città disponibili, assegnare ad ognuna un peso e pescare da questo set quando si vanno a fare delle modifiche

    preferenza driver #4 - modifiche al merchandise
    idea - definire per ogni driver una gaussiana multivariata che determina, per ogni elemento, quanto il driver preferisca aggiungere o togliere, in percentuale

    preferenza driver #5 - numero di merchandise trasportata
    idea - definire se il driver vuole o meno aggiungere/togliere merch

    preferenza driver #6 - trip in cui la merch cambia
    idea - definire se il driver vuole o meno aggiungere/togliere merch in uno specifico trip, visto che certi trip potrebbero non cambiare assolutamente
    """
    actual_routes = generate_actual_routes()
    json_output = json.dumps(actual_routes, indent=4)

    # Print the JSON output
    output = open("data/actual_normal.json", "w")
    output.write(json_output)