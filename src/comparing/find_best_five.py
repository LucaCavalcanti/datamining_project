'''
a file called driver.json that has for each driver we need to find the 5 standard routes that if the driver does them,
it minimizes the diversion.
You can test this by considering as pool of standard routes those that originally the company has and also that you recommend in the
recStandard.json.

The file driver.json has the following sintax:
[
    {driver: C, routes: [s10, s20, s2, s6, s10]},
    {driver: A, routes: [s1, s2, s22, s61, s102]},
    ...
]

todo:
I need to compare every actual made by the driver with the standards and store every result into a sorted list and take the five best
    dict<list, int>
'''

import json
import sys
sys.path.append('src/clustering/BFR/feature_extraction')
from similarity import similarity
from feature_extractions import get_features

def get_standards():
    '''to test
    
    get the standard routes'''
    with open(standard_file) as json_file:
        standard_routes = json.load(json_file)
    return standard_routes

#standard_routes = get_standards()

def get_actual():
    '''to test
    
    get the actual routes'''
    with open(actual_file) as json_file:
        actual_routes = json.load(json_file)
    return actual_routes

#actual_routes = get_actual()

def get_drivers(actual_routes: dict):
    '''
    get the list of drivers
    '''
    drivers = set()
    for route in actual_routes:
        drivers.add(route['driver'])
    return drivers

#drivers = get_drivers()

def get_actual_to_driver(driver_id: int, actual_routes: dict):
    '''
    get the actual routes associated to the given driver
    '''
    actuals = list()
    for route in actual_routes:
        if route['driver'] == driver_id:
            actuals.append(route)
    return actuals


def compare_routes(standards : list, actuals : list):
    '''
    input:
        - standards: pool of standard those that originally the company has and also that are recommend in the recStandard.json
        - actuals: routes made by the driver
    
    output:
        - best_five: list of the best five standard routes for the driver
    '''
    
    similarity_dict = dict()
    
    for standard in standards:
        cities = list()
        merchandise = list()
        for actual in actuals:
            city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch = get_features(standard, actual)
            city_similarity, merch_similarity = similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch)
            cities.append(city_similarity)
            merchandise.append(merch_similarity)
        cosine = (sum(cities) / len(cities)) + (sum(merchandise) / len(merchandise))
        similarity_dict[standard['id']] = cosine

    sorted_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))
    
    best_five = list()
    for route in sorted_dict:
        if len(best_five) == 5:
            break
        best_five.append(route)
    return best_five

def find_best_five_per_driver(standard_routes, actual_routes, result_file: str):
    output = open(result_file, 'w')
    output.write('[\n')
    
    drivers = get_drivers(actual_routes)
    
    counter = 0
    for driver in drivers:
        actuals = get_actual_to_driver(driver, actual_routes)
        best_five = compare_routes(standard_routes, actuals)
        
        json_output = json.dumps({"driver": driver, "routes": best_five})
        
        output.write(json_output)
        if counter == len(drivers) - 1:
            output.write('\n')
        else:
            output.write(',\n')
        counter += 1
        
    output.write(']')

if __name__ == "__main__":
    standard_file = 'data/small2/standard_small.json'
    actual_file = 'data/small2/actual_normal_small.json'
    result_file = 'results/driver_normal_small.json'
    standards = get_standards()
    actuals = get_actual()
    find_best_five_per_driver(standards, actuals, result_file)
