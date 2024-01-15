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
import ijson
from time import time
import sys
sys.path.append('src/clustering/similarities')
from similarity import similarity
from feature_extractions import get_features

time_start = None
compare_routes_times = []
sort_routes_times = []
drivers_times = []
custom_distances_times = []

def get_elapsed_time():
    time_now = time()
    # return with two decimals precision
    return round(time_now - time_start, 2)

def get_routes(standard_file: str):
    '''to test
    
    get the routes'''
    with open(standard_file) as json_file:
        routes = json.load(json_file)
    return routes


#actual_routes = get_actual()

def get_drivers(actual_routes: str):
    '''
    get the list of drivers
    '''
    drivers = set()
    with open(actual_routes, "rb") as f:
        for route in ijson.items(f, "item"):
            drivers.add(route['driver'])
    return drivers

#drivers = get_drivers()

def get_actual_to_driver(driver_id: int, actual_routes: dict):
    '''
    get the actual routes associated to the given driver
    '''
    actuals = list()
    with open(actual_routes, "rb") as f:
        for route in ijson.items(f, "item"):
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
    
    time_temp = time()
    for standard in standards:
        cosines = list()
        for actual in actuals:
            time_temp2 = time()
            city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch = get_features(standard, actual)
            merch_similarity, city_similarity = similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch)
            total_cosine = (city_similarity * (1 - city_weight)) + (merch_similarity * (1 - merch_weight))
            cosines.append(total_cosine)
            time_temp3 = time()
            custom_distances_times.append(time_temp3 - time_temp2)
        cosine = sum(cosines) / len(cosines)
        similarity_dict[standard['id']] = cosine
    time_temp4 = time()
    compare_routes_times.append(time_temp4 - time_temp)

    time_temp = time()
    sorted_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))
    time_temp2 = time()
    sort_routes_times.append(time_temp2 - time_temp)

    print('list of cosine similarity related to the standard:\n', sorted_dict)
    
    best_five = list()
    for route in sorted_dict:
        if len(best_five) == 5:
            break
        best_five.append(route)
    return best_five

def find_best_five_per_driver(standard_routes, actual_routes_file, rec_standard, result_file: str, city_weight: int, merch_weight: int):
    global time_start
    time_start = time()

    output = open(result_file, 'w')
    output.write('[\n')
    
    drivers = get_drivers(actual_routes_file)
    
    time_temp = time()
    counter = 0
    standards = standard_routes + rec_standard
    for driver in drivers:
        actuals = get_actual_to_driver(driver, actual_routes_file)
        best_five = compare_routes(standards, actuals, city_weight, merch_weight)
        
        json_output = json.dumps({"driver": driver, "routes": best_five})
        
        output.write(json_output)
        if counter == len(drivers) - 1:
            output.write('\n')
        else:
            output.write(',\n')
        counter += 1
        
    output.write(']')
    output.close()
    time_temp2 = time()
    drivers_times.append(time_temp2 - time_temp)

    print('Average time taken to compute custom distances:', sum(custom_distances_times) / len(custom_distances_times))
    print('Average time taken to compare routes:', sum(compare_routes_times) / len(compare_routes_times))
    print('Average time taken to sort routes:', sum(sort_routes_times) / len(sort_routes_times))
    print('Average time taken to find drivers:', sum(drivers_times) / len(drivers_times))
    print('Total time taken:', get_elapsed_time())

if __name__ == "__main__":
    standard_file = 'data/big/standard_big.json'
    actual_file = 'data/big/actual_big.json'
    result_file = 'results/driver_normal_TEST.json'
    recStandard_file = 'results/recStandard_big.json'
    standards = get_routes(standard_file)
    actuals = get_routes(actual_file)
    recStandard = get_routes(recStandard_file)
    find_best_five_per_driver(standards, actuals, recStandard, result_file, 0.7196538657216474, 0.28034613427835264)
