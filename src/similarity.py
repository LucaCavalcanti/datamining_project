'''
we need to:
- find a measure of similarity between routes
- cluster the routes


find a measure of similarity
we can consider a route as a vector of 0s and 1s where
- 0 indicates that the city is not present in the route
- 1 indicates that the city is present in the route

in this way we can compare an actual route with a standard route and understand how many they are different
cosine distance?
p1 = 00111  p2 = 10011
p1p2 = 2 (two 1s in common) |p1| = |p2| = sqrt(3) (three 1s in the vector)
cos a = 2/3     a = 48 degree
'''

import json
import sys
import numpy as np
from numpy.linalg import norm

number_of_cities = int(sys.argv[1])

def get_standard(standard_id: str):
    '''get the standard routes'''
    with open("data/standard3.json") as json_file:
        standard_routes = json.load(json_file)
    for route in standard_routes:
        if route["id"] == standard_id:
            return route
    return []

def get_actual():
    '''get the actual routes'''
    with open("data/actual_preference.json") as json_file:
        actual_routes = json.load(json_file)
    return actual_routes

def get_cities(number_of_cities: int) -> list:
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

'''
get actual
get standard related to the actual
convert the actual into a vector
convert the standard into a vector
'''

def create_vector_cities(route: list) -> set:
    cities_route: set = set()
    for trip in route:
        cities_route.add(trip['from'])
        cities_route.add(trip['to'])
    return cities_route

def create_similarity_vector(route: dict, cities: list) -> list:
    if isinstance(route, dict):
        route_vector: set = create_vector_cities(route['route'])
        similarity_vector: list = []
        for city in cities:
            similarity_vector.append(1) if city in route_vector else similarity_vector.append(0)
        return similarity_vector
    else:
        return []

if __name__ == "__main__":
    actual_routes = get_actual()
    cities = get_cities(number_of_cities)
    for route in actual_routes:
        standard_route = get_standard(route['sroute'])
        actual_similarity = create_similarity_vector(route, cities)
        standard_similarity = create_similarity_vector(standard_route, cities)
        A = np.array(actual_similarity)
        B = np.array(standard_similarity)
        cosine = np.dot(A, B)/ (norm(A)*norm(B))
        print(route['id'], route['sroute'], cosine)
