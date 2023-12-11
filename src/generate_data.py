import json
import sys
import random

# Take from command line the number of routes to generate
number_of_routes = int(sys.argv[1])

# Take from command line the number of cities to generate
number_of_cities = int(sys.argv[2])

# Take from command line the maxnumber of trips per route
max_route_len = int(sys.argv[3])

MIN_MERCH = 1
MAX_MERCH = 50

with open("data/merchandise/merchandise_small.json") as merch_file:
    merchandise_global = json.load(merch_file)

def generate_cities(number_of_cities):
    cities_file = open("data/cities/worldcities.csv", "r")
    cities = []
    cities_file.readline()
    counter = 0
    for cities_file_line in cities_file.readlines():
        if counter == number_of_cities:
            break
        cities.append(cities_file_line.split(",")[1].replace('"',''))
        counter += 1
    return cities

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

def generate_trips(cities, max_route_len):
    trips = []
    merchandise = {}
    from_city = cities[random.randint(0, len(cities) - 1)]
    for k in range(random.randint(1, max_route_len)):
        to_city = cities[random.randint(0, len(cities) - 1)]
        while from_city == to_city:
            to_city = cities[random.randint(0, len(cities) - 1)]
        merchandise = {}
        for j in range(random.randint(1, len(merchandise_global))):
            merchandise[random.choice(merchandise_global)] = random.randint(MIN_MERCH, MAX_MERCH)
        trips.append({"from": from_city, "to": to_city, "merchandise": merchandise})
        from_city = to_city
    return trips

def generate_routes(number_of_routes, cities, max_route_len):
    routes = []
    for i in range(number_of_routes):
        routes.append({"id": "s" + str(i), "route": generate_trips(cities, max_route_len)})
    return routes

if __name__ == '__main__':
    cities = generate_italian_cities(number_of_cities)
    routes = generate_routes(number_of_routes, cities, max_route_len)
    json_output = json.dumps(routes, indent=4)

    # Print the JSON output
    output = open("data/small/standard_small.json", "w")
    output.write(json_output)