import json
import sys
import random

# Take from command line the number of routes to generate
number_of_routes = int(sys.argv[1])

# Take from command line the number of cities to generate
number_of_cities = int(sys.argv[2])

# Take from command line the maxnumber of trips per route
max_route_len = int(sys.argv[3])

class Trip:
    def __init__(self, from_city, to_city, merchandise):
        self.from_city = from_city
        self.to_city = to_city
        self.merchandise = merchandise
    def __str__(self):
        return f'{{"from": "{self.from_city}", "to": "{self.to_city}", "merchandise": {self.merchandise}}}'

class Route:
    def __init__(self, id, trips):
        self.id = "s" + str(id)
        self.route = trips
    def __str__(self):
        routes = "["
        for i in range(len(self.route)):
            routes = routes + str(self.route[i])
            if (i != len(self.route) - 1):
                routes += ",\n"
            else:
                routes += "\n"
        routes += "]"
        return f'{{"id": "{self.id}", "route": {routes}}}'

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

def generate_trips(cities, max_route_len):
    trips = []
    merchandise = {}
    from_city = cities[random.randint(0, len(cities) - 1)]
    for k in range(random.randint(1, max_route_len)):
        to_city = cities[random.randint(0, len(cities) - 1)]
        while from_city == to_city:
            to_city = cities[random.randint(0, len(cities) - 1)]
        merchandise = {}
        for j in range(random.randint(1, 10)):
            merchandise[random.choice(["milk", "butter", "pens", "tomatoes", "honey", "bread"])] = random.randint(1, 100)
        trips.append({"from": from_city, "to": to_city, "merchandise": merchandise})
        from_city = to_city
    return trips

def generate_routes(number_of_routes, cities, max_route_len):
    routes = []
    for i in range(number_of_routes):
        routes.append({"id": "s" + str(i), "route": generate_trips(cities, max_route_len)})
    return routes

if __name__ == '__main__':
    cities = generate_cities(number_of_cities)
    routes = generate_routes(number_of_routes, cities, max_route_len)
    json_output = json.dumps(routes, indent=4)

    # Print the JSON output
    output = open("data/standard.json", "w")
    output.write(json_output)

# # Creating the dictionary structure
# data = [
#     {
#         "id": "s5",
#         "route": [
#             {"from": "Rome", "to": "Milan", "merchandise": {"milk": 3, "pens": 10, "butter": 20}},
#             {"from": "Milan", "to": "Verona", "merchandise": {"milk": 5, "honey": 9, "butter": 10, "tomatoes": 20}},
#             {"from": "Verona", "to": "Venezia", "merchandise": {"butter": 7, "pens": 2, "tomatoes": 10}}
#         ]
#     },
#     {
#         "id": "s10",
#         "route": [
#             {"from": "Rome", "to": "Milan", "merchandise": {"milk": 2, "pens": 10, "butter": 20}},
#             {"from": "Milan", "to": "Verona", "merchandise": {"milk": 5, "tomatoes": 24}},
#             {"from": "Verona", "to": "Venezia", "merchandise": {"butter": 7, "bread": 2, "tomatoes": 10}}
#         ]
#     }
# ]

# # Create 

# # Convert the dictionary to JSON
# json_output = json.dumps(data, indent=4)

# # Print the JSON output
# print(json_output)

# print(cities[0])