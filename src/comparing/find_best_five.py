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
sys.path.append('src/clustering/similarities')
from similarity import similarity
from feature_extractions import get_features

def get_routes(standard_file: str):
    '''to test
    
    get the routes'''
    with open(standard_file) as json_file:
        routes = json.load(json_file)
    return routes


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


def compare_routes(standards : list, actuals : list, city_weight: int, merch_weight: int):
    '''
    input:
        - standards: pool of standard those that originally the company has and also that are recommend in the recStandard.json
        - actuals: routes made by the driver
    
    output:
        - best_five: list of the best five standard routes for the driver
    '''
    
    similarity_dict = dict()
    
    for standard in standards:
        cosines = list()
        for actual in actuals:
            city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch = get_features(standard, actual)
            merch_similarity, city_similarity = similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch)
            total_cosine = (city_similarity * (1 - city_weight)) + (merch_similarity * (1 - merch_weight))
            cosines.append(total_cosine)
        cosine = sum(cosines) / len(cosines)
        similarity_dict[standard['id']] = cosine

    sorted_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))
    print('list of cosine similarity related to the standard:\n', sorted_dict)
    
    best_five = list()
    for route in sorted_dict:
        if len(best_five) == 5:
            break
        best_five.append(route)
    return best_five

def find_best_five_per_driver(standard_routes, actual_routes, rec_standard, result_file: str, city_weight: int, merch_weight: int):
    output = open(result_file, 'w')
    output.write('[\n')
    
    drivers = get_drivers(actual_routes)
    
    counter = 0
    standards = standard_routes + rec_standard
    for driver in drivers:
        actuals = get_actual_to_driver(driver, actual_routes)
        best_five = compare_routes(standards, actuals, city_weight, merch_weight)
        
        json_output = json.dumps({"driver": driver, "routes": best_five})
        
        output.write(json_output)
        if counter == len(drivers) - 1:
            output.write('\n')
        else:
            output.write(',\n')
        counter += 1
        
    output.write(']')

if __name__ == "__main__":
    """ standard_file = 'data/small2/standard_small.json'
    actual_file = 'data/small2/actual_normal_small.json'
    result_file = 'results/driver_normal_small.json'
    recStandard_file = 'results/recStandard_normal_small.json'
    standards = get_routes(standard_file)
    actuals = get_routes(actual_file)
    recStandard = get_routes(recStandard_file)
    find_best_five_per_driver(standards, actuals, recStandard, result_file) """
