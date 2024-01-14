import json
import sys

sys.path.append('src/clustering')
from bfr import BFR

sys.path.append('src/comparing')
from find_best_five import find_best_five_per_driver
from find_perfect_route import find_perfect_route_per_driver

from time import time
from pathlib import Path
import os

# GLOBAL VARIABLES
# type_file = int(sys.argv[1])

def get_route(standard_file: str):
    '''
    get the standard routes
    '''
    # check if file exists
    if not Path(standard_file).is_file():
        print('Please provide the correct file path to the route file. Wrong path: ' + standard_file)
        exit()

    with open(standard_file) as json_file:
        routes = json.load(json_file)
    return routes


def data_mining():
    '''
    it is required to insert in the command line the standard and the actual routes you want use.
    if you want to test the code you can insert the word 'test' as the first argument and the type of the files you want to test as the second argument.
    the type of the files can be:
        - small
        - small_normal
        - big
        - big_normal

    then the function calls:
        - the function BFR from bfr.py and create the file recStandard.json for the required dataset
        - the function find_best_five_per_driver from find_best_five.py and create the file 
        - the function
    '''
    
    standard_file = ''
    actual_file = ''
    rec_standard_file = ''
    driver = ''
    perfect_route = ''

    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print('Wrong number of arguments, usage: main.py [standard_file_path] [actual_file_path]')
        exit()

    # get from input the type of file
    standard_file = sys.argv[1]
    actual_file = sys.argv[2]

    if standard_file == 'test':
        type_file = actual_file
        if type_file == 'small':
            standard_file = os.path.join('data', 'small', 'standard_small.json')
            actual_file = os.path.join('data', 'small', 'actual_small.json')
            
            rec_standard_file = os.path.join('results', 'recStandard_small.json')
            driver = os.path.join('results', 'driver_small.json')
            perfect_route = os.path.join('results', 'perfectRoute_small.json')
        elif type_file == 'small_normal':
            standard_file = os.path.join('data', 'small', 'standard_small.json')
            actual_file = os.path.join('data', 'small', 'actual_small_normal.json')
            
            rec_standard_file = os.path.join('results', 'recStandard_small_normal.json')
            driver = os.path.join('results', 'driver_small_normal.json')
            perfect_route = os.path.join('results', 'perfectRoute_small_normal.json')
        elif type_file == 'big':
            standard_file = os.path.join('data', 'big', 'standard_big.json')
            actual_file = os.path.join('data', 'big', 'actual_big.json')
            
            rec_standard_file = os.path.join('results', 'recStandard_big.json')
            driver = os.path.join('results', 'driver_big.json')
            perfect_route = os.path.join('results', 'perfectRoute_big.json')
        elif type_file == 'big_normal':
            standard_file = os.path.join('data', 'big', 'standard_big.json')
            actual_file = os.path.join('data', 'big', 'actual_big_normal.json')
            
            rec_standard_file = os.path.join('results', 'recStandard_big_normal.json')
            driver = os.path.join('results', 'driver_big_normal.json')
            perfect_route = os.path.join('results', 'perfectRoute_big_normal.json')
        else:
            print('Wrong type of file, usage for testing purposes: main.py [test] [small, small_normal, big, big_normal]')
            exit()
    else:
        # take the actual route name as a string taken from the last /
        actual_route_name = actual_file.split(os.sep)[-1].split('.')[0]
        actual_route_name = actual_route_name.replace('actual', '')
        rec_standard_file = os.path.join('results', 'recStandard') + actual_route_name + '.json'
        driver = os.path.join('results', 'driver') + actual_route_name + '.json'
        perfect_route = os.path.join('results', 'perfectRoute') + actual_route_name + '.json'
        
    # get the list of standards
    standard = get_route(standard_file)
    
    # get the list of actuals
    actual = get_route(actual_file)
        
    start_time = time()
    # recStandard
    print('=====BFR=====')
    city_weight, merch_weight = BFR(standard_file, actual_file, rec_standard_file)
    
    # get the list of rec standards
    rec_standard = get_route(rec_standard_file)
    
    # driver
    print('\n\n=====DRIVER=====')
    find_best_five_per_driver(standard, actual, rec_standard, driver, city_weight, merch_weight)

    # perfectRoute
    temp_time = time()
    print('\n\n=====PERFECT ROUTE=====')
    find_perfect_route_per_driver(actual, perfect_route, city_weight, merch_weight)
    temp_time2 = time()
    print('time taken, top 5:', temp_time2 - temp_time)
    
    end_time = time()
    print('total time taken:', end_time - start_time)

if __name__ == '__main__':
    data_mining()