
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

def similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch):
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
    # city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch, _, _ = fe.get_features(standard_route, actual_route)
    
    A = np.array(standard_cities)
    B = np.array(actual_cities)
    city_cosine = np.dot(A, B) / (norm(A) * norm(B))
    
    cosines = list()
    # print(np.array(standard_cities))
    # print(np.array(actual_cities))
    # print("=====")
    for index in range(len(standard_cities)):
        # if the city is not present in both routes we skip it
        if standard_cities[index] == 0 and actual_cities[index] == 0: continue

        # if the city is present in both the routes:
        # if the city count is different pair up the closest merch vectors, and pair the rest of the merch vectors with null vectors
        # if the city count is equal compute the cosine similarity pairwise between vectors
        
        # take all the vectors related to the city
        standard = search_city_vectors(standard_merch, merch_indexes, city_indexes[index])
        actual = search_city_vectors(actual_merch, merch_indexes, city_indexes[index])

        penalty = 1
        
        new_standard = []
        new_actual = []
        # normalize the vectors to have the same length, and for items at the same index to be the closest possible
        if len(standard) > len(actual):
            # driver missed some cities
            penalty = 0.5
            # sort the vectors by cosine similarity - put at the same indexes the closest vectors, pair the outliers with the null vector
            for i in range(len(actual)):
                max_cosine = 0
                max_index = 0
                for j in range(len(standard)):
                    A = np.array(standard[j])
                    B = np.array(actual[i])
                    cosine = np.dot(A, B)/ (norm(A) * norm(B))
                    if cosine > max_cosine:
                        max_cosine = cosine
                        max_index = j
                new_standard.append(standard[max_index])
                new_actual.append(actual[i])
                standard.pop(max_index)
            for i in range(len(standard)):
                new_standard.append(standard[i])
                new_actual.append(create_vector_for_absent_city(standard[i], merch_indexes, city_indexes[index]))
            standard = new_standard
            actual = new_actual
        elif len(actual) > len(standard):
            # driver added some cities
            penalty = 0.75
            # sort the vectors by cosine similarity - put at the same indexes the closest vectors, pair the outliers with the null vector
            for i in range(len(standard)):
                max_cosine = 0
                max_index = 0
                for j in range(len(actual)):
                    A = np.array(standard[i])
                    B = np.array(actual[j])
                    cosine = np.dot(A, B)/ (norm(A) * norm(B))
                    if cosine > max_cosine:
                        max_cosine = cosine
                        max_index = j
                new_standard.append(standard[i])
                new_actual.append(actual[max_index])
                actual.pop(max_index)
            for i in range(len(actual)):
                new_standard.append(create_vector_for_absent_city(actual[i], merch_indexes, city_indexes[index]))
                new_actual.append(actual[i])
            standard = new_standard
            actual = new_actual
        # print the full vectors using numpy array
        # print("city: ", city_indexes[index])
        # print(np.array(standard))
        # print("-----")
        # print(np.array(actual))
        # print("\n\n")
        # if the city count is equal pair up the closest merch vectors and compute the cosine similarity
        if len(standard) == len(actual):
            for i in range(len(standard)):
                A = np.array(standard[i])
                B = np.array(actual[i])
                cosine = np.dot(A, B)/ (norm(A) * norm(B))
                cosine = cosine * penalty
                cosines.append(cosine)


    merch_cosine = sum(cosines) / len(cosines)
    # print(cosine_mean)
    return merch_cosine, city_cosine

'''
if standard_cities[index] == 1:
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
'''

def search_city_vectors(route: list, merch_index: list, city: str):
    '''
    function that searches the vectors of merch related to the city
    
    input:
        - route: list of merch with respective cities
        - merch_index: list of labels for the route list
        - city: city to search
        
    output:
        - vector: list(s) of merch quantity related to the city
    '''
    vectors = []
    for index in range(len(merch_index)):
        # print(merch_index[index], city)
        if merch_index[index] == city:
            # print(merch_index[index], city)

            for vector in route:
                if vector[index] == 1:
                    vectors.append(vector)
    return vectors

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