import json
import sys

sys.path.append('src/clustering/BFR')
from bfr import BFR

sys.path.append('src/comparing')
from find_best_five import find_best_five_per_driver
from find_perfect_route import find_perfect_route_per_driver

# GLOBAL VARIABLES
type_file = int(sys.argv[1])

def get_standards(standard_file: str):
    '''
    get the standard routes
    '''
    with open(standard_file) as json_file:
        standard_routes = json.load(json_file)
    return standard_routes

def get_actual(actual_file: str):
    '''
    get the actual routes
    '''
    with open(actual_file) as json_file:
        actual_routes = json.load(json_file)
    return actual_routes

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
    rec_standard = ''
    driver = ''
    perfect_route = ''
    
    if type_file == 'small':
        standard_file = 'data/standard_small.json'
        actual_file = 'data/actual_small.json'
        rec_standard = 'results/recStandard_small.json'
        driver = 'results/driver_small.json'
        perfect_route = 'results/perfectRoute_small.json'
    elif type_file == 'normal_small':
        standard_file = 'data/standard_normal_small.json'
        actual_file = 'data/actual_normal_small.json'
        rec_standard = 'results/recStandard_normal_small.json'
        driver = 'results/driver_normal_small.json'
        perfect_route = 'results/perfectRoute_normal_small.json'
    elif type_file == 'big':
        standard_file = 'data/standard_big.json'
        actual_file = 'data/actual_big.json'
        rec_standard = 'results/recStandard_big.json'
        driver = 'results/driver_big.json'
        perfect_route = 'results/perfectRoute_big.json'
    else:
        standard_file = 'data/standard_normal_big.json'
        actual_file = 'data/actual_normal_big.json'
        rec_standard = 'results/recStandard_normal_big.json'
        driver = 'results/driver_normal_big.json'
        perfect_route = 'results/perfectRoute_normal_big.json'
        
    # get the list of standards
    standard = get_standards(standard_file)
    
    # get the list of actuals
    actual = get_actual(actual_file)
        
    # recStandard
    BFR(standard, actual, rec_standard)
    
    # driver
    find_best_five_per_driver(standard, actual, driver)
    
    # perfectRoute
    find_perfect_route_per_driver(standard, actual, perfect_route)

if __name__ == '__main__':
    data_mining()