# every driver take a standard route but he will possibly change it according to his preferences
# we need to create a new json file in which we associate to each driver a standard route and we wrote
# the route that he takes (so we write the changes that he makes to the standard route and the changes that he makes
# in the delivery of the merchandise)
# first of all we take a standard route and we assign it to a driver

import json
import random
import sys

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

def print_actual_route(actual_route, position, trip):
    counter = 0
    print(actual_route["id"])
    print("current trip: ", trip["from"], " ", trip["to"])
    print(actual_route["route"][0]["from"])
    for trip in actual_route["route"]:
        if counter == position:
            print(trip["from"], "<------")
            print(trip["to"], "<------")
        else:
            print(trip["from"])
            print(trip["to"])
        counter += 1
    print("\n")

def associate_driver(standard_routes):
    for driver in range(drivers):
        driver_name = chr(ord("A") + driver)
        print(driver_name)
        # select a random standard route
        standard_routes = get_standard()
        actual_route = standard_routes[random.randint(0, len(standard_routes) - 1)]
        # modify the standard route according to the driver preferences
        # for each city of the route choose in a random way if keep the city or skip it or change it and with which city
        counter = 0
        for trip in (actual_route["route"]):
            #print("start of for cycle, counter: ", counter)
            # print_actual_route(actual_route, counter, trip)
            if random.randint(0, 1) == 0:
                # change the city or skip it or add it
                if random.randint(0, 1) == 0:
                    # change the city
                    #print("Changing a city.")
                    trip["to"] = cities[random.randint(0, len(cities) - 1)]
                    if counter+1 < len(actual_route["route"]):
                        actual_route["route"][counter+1]["from"] = trip["to"]
                else:
                    # skip the city
                    #print("Skipping a city.")
                    if counter+1 < len(actual_route["route"]):
                        trip["to"] = actual_route["route"][counter+1]["to"]
                        # counter+=1
                        del actual_route["route"][counter+1]
            else:
                if random.randint(0, 1) == 0:
                    # add the city
                    if counter > 0:
                        merchandise = {}
                        for j in range(random.randint(1, 30)):
                            merchandise[random.choice(["milk", "butter", "pens", "tomatoes", "honey", "bread", "pasta", "spaghetti", "pizza", "cookies", "salad", "tortel", 
                                                        "coca-cola", "water", "sparkling water", "orange juice", "arancini", "fanta", "beer", "computer", "phone", "car",
                                                        "train", "sweater", "egg", "carrot", "rice", "soup" , "t-shirt", "jeans", "eyeglasses", "sugar", "salt", "pepper",
                                                        "oil", "rosemary", "thime", "curry", "pepper", "gloves", "spoon", "fork", "knife", "pot", "pan", "wine", "grappa" 
                                                        ])] = random.randint(1, 100)
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
            #print("--------------\n")
        print(actual_route)



if __name__ == '__main__':
    standard_routes = get_standard()
    cities = generate_italian_cities(number_of_cities)
    associate_driver(standard_routes)