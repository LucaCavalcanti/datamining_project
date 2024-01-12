import json
import sys

sys.path.append('src/clustering')
from bfr import BFR

sys.path.append('src/comparing')
from find_best_five import find_best_five_per_driver
from find_perfect_route import find_perfect_route_per_driver

from time import time

# GLOBAL VARIABLES
type_file = int(sys.argv[1])

def get_route(standard_file: str):
    '''
    get the standard routes
    '''
    with open(standard_file) as json_file:
        routes = json.load(json_file)
    return routes


def data_mining():
    '''
    it is required to insert in the command line the type of datasets you want use:
        - 'small'
        - 'normal_small'
        - 'big'
        - 'normal_big'
        
    thenthe function calls:
        - the function BFR from bfr.py and create the file recStandard.json for the required dataset
        - the function find_best_five_per_driver from find_best_five.py and create the file 
        - the function
    '''
    
    standard_file = ''
    actual_file = ''
    rec_standard_file = ''
    driver = ''
    perfect_route = ''
    
    if type_file == 'small':
        standard_file = 'data/standard_small.json'
        actual_file = 'data/actual_small.json'
        rec_standard_file = 'results/recStandard_small.json'
        driver = 'results/driver_small.json'
        perfect_route = 'results/perfectRoute_small.json'
    elif type_file == 'normal_small':
        standard_file = 'data/standard_normal_small.json'
        actual_file = 'data/actual_normal_small.json'
        rec_standard_file = 'results/recStandard_normal_small.json'
        driver = 'results/driver_normal_small.json'
        perfect_route = 'results/perfectRoute_normal_small.json'
    elif type_file == 'big':
        standard_file = 'data/standard_big.json'
        actual_file = 'data/actual_big.json'
        rec_standard_file = 'results/recStandard_big.json'
        driver = 'results/driver_big.json'
        perfect_route = 'results/perfectRoute_big.json'
    else:
        standard_file = 'data/standard_normal_big.json'
        actual_file = 'data/actual_normal_big.json'
        rec_standard_file = 'results/recStandard_normal_big.json'
        driver = 'results/driver_normal_big.json'
        perfect_route = 'results/perfectRoute_normal_big.json'
        
    # get the list of standards
    standard = get_route(standard_file)
    
    # get the list of actuals
    actual = get_route(actual_file)
        
    start_time = time()
    # recStandard
    city_weight, merch_weight = BFR(standard, actual, rec_standard_file)
    
    # get the list of rec standards
    rec_standard = get_route(rec_standard_file)
    
    # driver
    find_best_five_per_driver(standard, actual, rec_standard, driver, city_weight, merch_weight)
    
    # perfectRoute
    find_perfect_route_per_driver(standard, actual, perfect_route)
    
    end_time = time()
    print(end_time - start_time)

if __name__ == '__main__':
    data_mining()