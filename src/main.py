import json
import sys
sys.path.append('src/clustering/BFR')
from bfr import BFR

# GLOBAL VARIABLES
type_file = int(sys.argv[1])

def get_standards(standard_file: str):
    '''
    get the standard routes
    '''
    with open("data/small2/" + standard_file) as json_file:
        standard_routes = json.load(json_file)
    return standard_routes

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
    
    standard = ''
    actual = ''
    rec_standard = ''
    driver = ''
    perfect_route = ''
    
    if type_file == 'small':
        standard = 'standard_small.json'
        actual = 'actual_small.json'
        rec_standard = 'result/recStandard_small.json'
        driver = 'driver_small.json'
        perfect_route = 'perfectRoute_small.json'
    elif type_file == 'normal_small':
        standard = 'standard_normal_small.json'
        actual = 'actual_normal_small.json'
        rec_standard = 'result/recStandard_normal_small.json'
        driver = 'driver_normal_small.json'
        perfect_route = 'perfectRoute_normal_small.json'
    elif type_file == 'big':
        standard = 'standard_big.json'
        actual = 'actual_big.json'
        rec_standard = 'result/recStandard_big.json'
        driver = 'driver_big.json'
        perfect_route = 'perfectRoute_big.json'
    else:
        standard = 'standard_normal_big.json'
        actual = 'actual_normal_big.json'
        rec_standard = 'result/recStandard_normal_big.json'
        driver = 'driver_normal_big.json'
        perfect_route = 'perfectRoute_normal_big.json'
        
    #BFR(standard, actual, rec_standard)
    
    

if __name__ == '__main__':
    data_mining()