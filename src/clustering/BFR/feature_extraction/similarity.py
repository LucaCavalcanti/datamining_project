
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

import numpy as np
from numpy.linalg import norm
from feature_extraction import get_features

def calculate_similarity(standard_route, actual_route):
    '''
    input:
        - standard_route: standard route
        - actual_route: actual_route
    
    output:
        - similarity: similarity between route A and route B given the similarity of the cities and the list of merch
    
    reasoning:
        - if a city is in both the route we check whether the merch has been respected or the driver has changed his quantity
        - if a city is present only in the standard route than we multiply for a certain weight the error
        - if a city is present only in the actual route than we multiply for another weight the error
    '''
    city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch, _, _ = get_features(standard_route, actual_route)
    
    A = np.array(standard_cities)
    B = np.array(actual_cities)
    route_cosine = np.dot(A, B) / (norm(A) * norm(B))
    
    cosines = list()
    for index in range(len(standard_cities)):
        if standard_cities[index] > 0:
            standard = search_city_vector(standard_merch, merch_indexes, city_indexes[index])
            # if the list is empty then the city is the starting point of the route
            if len(standard) == 0: continue
        if actual_cities[index] > 0:
            actual = search_city_vector(actual_merch, merch_indexes, city_indexes[index])
            # if the list is empty then the city is the starting point of the route
            if len(actual) == 0: continue
        if standard_cities[index] == 0:
            standard = np.array(create_vector_for_absent_city(actual, merch_indexes, city_indexes[index]))
        if actual_cities[index] == 0:
            actual = np.array(create_vector_for_absent_city(standard, merch_indexes, city_indexes[index]))
        A = np.array(standard)
        B = np.array(actual)
        cosine = np.dot(A, B) / (norm(A) * norm(B))
        if standard_cities[index] == 0:
            cosine = cosine * 0.75
        if actual_cities[index] == 0:
            cosine = cosine * 0.5
        cosines.append(cosine)
    cosine_mean = sum(cosines) / len(cosines)
    return cosine_mean, route_cosine

def search_city_vector (route: list, merch_index: list, city: str):
    '''
    function that research the vector related to the city (return empty list if the city is the starting point of the route)
    
    input:
        - route: list of merch and cities
        - merch_index: list of labels for the route list
        - city: city to search
        
    output:
        - vector: list of merch quantity related to the city
    '''
    for index in range(len(merch_index)):
        if merch_index[index] == city:
            for vector in route:
                if vector[index] == 1:
                    return vector
    return []

def create_vector_for_absent_city(other: list, merch_index: list, city : str):
    '''
    create a vector with only zeros for all the merch and a single 1 indicating the city
    
    input:
        - other: list of merch and cities refering to the other route (if we are analazing the actual the other is the standard)
        - merch_index: list of labels for the route list
        - city: city to search
        
    output:
        - vector: list of merch and cities
    '''
    vector = list()
    for index in range(len(other)):
        if merch_index[index] == city:
            vector.append(1)
        else:
            vector.append(0)
    return vector

if __name__ == "__main__":
    """ actual_routes = get_actual()
    for route in actual_routes:
        standard_route = get_standard(route['sroute'])
        actual_similarity = create_similarity_vector(route)
        standard_similarity = create_similarity_vector(standard_route)
        A = np.array(actual_similarity)
        B = np.array(standard_similarity)
        cosine = np.dot(A, B)/ (norm(A)*norm(B))
        print(route['id'], route['sroute'], cosine)
    actual_routes = get_actual()
    actual_route = actual_routes[0]
    actual_route_2 = actual_routes[1]
    standard_route = get_standard(actual_route['sroute'])
    merch_sim, city_sim = calculate_similarity(standard_route, standard_route)
    print(merch_sim, city_sim) """
