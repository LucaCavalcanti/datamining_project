'''
a file called perfectRoute.json that contains for each driver what would be the perfect ideal route.
The format of the file is as follow:

[
    {
        driver: C, route: [
            {from. Rome, to: Milan, merchandise: {milk: 4, pens: 4, butter: 20}}
            {from. Milan, to: Bergamo, merchandise: {milk: 5, honey: 19, butter: 10, tomatoes: 20}}
            {from. Bergamo, to: Venezia, merchandise: {butter: 47, pens: 2, tomatoes: 1}}
        ]
    },
    {
        driver: E, route: [
            {from. Bolzano, to: Trento, merchandise: {milk: 2, pens: 10, butter: 22}}
            {from. Trento, to: Verona, merchandise: {milk: 15, tomatoes: 4}}
            {from. Verona, to: Venezia, merchandise: {butter: 7, coca-cola: 21, tomatoes: 10}}
        ]
    },
]

dict<string, int>
dict<string, dict>
'''

import json
import random
import sys
from time import time
sys.path.append('src/clustering/similarities')
from similarity import similarity
from feature_extractions import get_features


def get_elapsed_time(start: float, end: float):
    return round(end - start, 15)


def get_route(actual_file: str):
    '''to test
    
    get the routes'''
    with open(actual_file) as json_file:
        routes = json.load(json_file)
    return routes

#actual_routes = get_actual()

def get_actual_to_driver(driver_id: int, actual_routes: dict):
    '''
    get the actual routes associated to the given driver
    '''
    actuals = list()
    for route in actual_routes:
        if route['driver'] == driver_id:
            actuals.append(route)
    return actuals

def get_drivers(actual_routes: dict):
    '''
    get the list of drivers
    '''
    drivers = set()
    for route in actual_routes:
        drivers.add(route['driver'])
    return drivers

#drivers = get_drivers()

def find_perfect_route(driver_id: int, actual_routes: dict):
    '''
    function to find the perfect route for a specific driver
    
    input:
        - driver_id: int
        
    output:
        - best_route: dict, the perfect route for the driver
    '''
    
    actuals = get_actual_to_driver(driver_id, actual_routes)
    
    
    total_cities = dict()
    data_merchandise = dict()
    
    '''
    data_merchandise = {
        'milano': {
            'length' : 3
            'mele': 3
            ...
        }
    }
    '''
    
    total_length = 0
    partial_length = 0
    time_data = 0
    for actual in actuals:
        cities = dict()
        merchandise = dict()
        total_length += 1
        partial_length += 1
        add_city(actual['route'][0]['from'], cities)
        for trip in actual['route']:
            city = trip['to']
            add_city(city, cities)
            total_length += 1
            partial_length += 1
            if city not in merchandise:
                merchandise[city] = dict()
            for merch in trip['merchandise']:
                if merch in merchandise:
                    merchandise[city][merch] += trip['merchandise'][merch]
                else:
                    merchandise[city][merch] = trip['merchandise'][merch]
        start_data_analyzation = time()
        analize_merch(merchandise, cities, data_merchandise)
        sum_mean_cities(total_cities, cities, partial_length)
        end_data_analyzation = time()
        time_data += (get_elapsed_time(start_data_analyzation, end_data_analyzation))
        partial_length = 0
    
    print('time to analyze data given by the actuals', time_data)
    new_route_length = int(total_length / len(actuals))
    
    start_sorting = time()
    sorted_cities = dict(sorted(total_cities.items(), key=lambda item: item[1], reverse=True))
    end_sorting = time()
    print('time to sort the dictionary containing the cities information:', get_elapsed_time(start_sorting, end_sorting))
    
    # take the n cities in order to create the new route where n is the length calculate in new_route_length
    cities_to_insert = list()
    for city in sorted_cities:
        if (len(cities_to_insert) == new_route_length):
            break
        if city in merchandise:
            times = int(sorted_cities[city] * new_route_length)
            for _ in range(times):
                cities_to_insert.append(city)
                
    cities_to_insert = scramble_list(cities_to_insert)
    new_route = {'driver': driver_id}
    trips = list()
    
    city = cities_to_insert[0]
    next_city = cities_to_insert[1]

    
    for index in range(new_route_length):
        
        if index != 0:
            city = next_city
            next_city = cities_to_insert[index]
        
        mean_merch = dict()
        add_merch(data_merchandise, mean_merch, next_city)
        trips.append({'from': city, 'to': next_city, 'merchandise': mean_merch})
    new_route['route'] = trips
    return new_route

def scramble_list(input_list):
    shuffled_list = input_list.copy()

    mcc = 0
    while any(shuffled_list[i] == shuffled_list[i + 1] for i in range(len(shuffled_list) - 1)):
        random.shuffle(shuffled_list)
        if mcc == 100:
            break
        mcc += 1

    return shuffled_list

""" 
def check_list(cities: list, length: int, sorted_cities: dict, sorted_index: int):
    print('check list')
    for city in cities:
        if sorted_cities[city] > length:
            
            print('Adjust the city: ', city)
            print('It compares ', sorted_cities[city], 'times')
            
            # number of substitution to do
            times = sorted_cities[city] - length
            
            # remove the city in eccessive quantity
            for _ in range(times):
                    cities.remove(city)
            
            while times > 0:
                
                # find the next city in the sorted list in order to substitute the other one and return also the number of times that we can repeat it
                next_city, times_new_city = find_next_city(sorted_cities, sorted_index)
                
                if times_new_city > times:
                    for _ in range(times):
                        cities.append(next_city)
                    times = 0
                else:
                    for _ in range(times_new_city):
                        cities.append(next_city)
                    times -= times_new_city

                sorted_index += 1


def find_next_city(sorted_cities: dict, sorted_index: int):
    index = 0
    for element in sorted_cities:
        if index == sorted_index + 1:
            return element, sorted_cities[element]
        index += 1
"""
'''
milano milano milano milano milano genova genova genova genova genova firenze

'''

def add_city(city: str, cities: dict):
    if city in cities:
        cities[city] += 1
    else:
        cities[city] = 1
        
def sum_mean_cities(total_cities: dict, cities: dict, length: int):
    for city in cities:
        if city in total_cities:
            total_cities[city] += (cities[city] / length)
        else:
            total_cities[city] = (cities[city] / length)
            
'''
3/10 milano
2/25 milano

0.33 + 0.08 = 0.41

3 milano -> 4 5 6
length -> 5
mele: 4, pere: 4, mandarini: 5, fichi: 2
mele: 4/15, pere: 4/15, mandarini: 5/15, fichi: 2/15
mele: 20/15 -> 1, pere: 20/15 -> 1, 25/15 -> 2, fichi: 10/15 -> 1

2 milano -> 4 5
length -> 4
mele: 3, pere: 3, mandarini: 3
mele: 3/9
mele: 1, pere: 1, mandarini: 2

length: 4
mele: 2, pere: 2, mandarini: 4, fichi: 1
mele: 1, pere: 1, mandarini: 2, fichi: 0

data_merchandise = {
        'milano': {
            'length' : 5
            'mele': 3
            ...
        }
    }
'''

def analize_merch(merchandise: dict, cities: dict, data_merchandise: dict):
    '''
    function to analize the quantity of the merch in the actual route and starts to adapt it for the perfect one
    
    input:
        - merchandise, dict: sum of merch for each city in the actual
        - cities, dict: number of times that a city compare in the actual
        - data_merchandise, dict: the dictionary in which we are going to store the data after we analize it
    '''
    # for all the cities present in the merchandise, so for all the cities that were in the actual just analized
    for city in merchandise:
        # if the city is already in the data_merchandise means that we have already inserted some information in one of the precedent routes
        
        total = 0 # used to calculate the total merchandise for that city in the whole route
        if city in data_merchandise:
            
            for merch in merchandise[city]:
                # sum the quantity of each merch in that city
                total += merchandise[city][merch]

            # sum and divide the length for the number of time we saw the city
            data_merchandise[city]['length'] += (total / cities[city])
            data_merchandise[city]['counter'] += 1
            
            # for all the merch present in the merchanise list we insert it in the data_merchandise divided for the total quantity of merchandise
            counter = 0
            partial_count = 0
            for merch in merchandise[city]:
                quantity = int((merchandise[city][merch] / total) * data_merchandise[city]['length'])
                partial_count += quantity
                if merch in data_merchandise[city]:
                    data_merchandise[city][merch] += quantity
                else:
                    data_merchandise[city][merch] = quantity
                # if there is a difference between the quantity inserted and the length we add/remove the quantity
                if counter == len(merchandise[city]) - 1 and partial_count != data_merchandise[city]['length']:
                    merchandise[city][merch] += (data_merchandise[city]['length'] - partial_count)
                counter += 1
        else:
            # if the city is not present in the dict means that this is the first time that we analize its data so we need to create the dict for the city
            data_merchandise[city] = dict()
            data_merchandise[city]['length'] = 0
            for merch in merchandise[city]:
                # sum the quantity of each merch in that city
                total += merchandise[city][merch]
            
            # sum and divide the length for the number of time we saw the city
            data_merchandise[city]['length'] = (total / cities[city])
            data_merchandise[city]['counter'] = 1
            
            # for all the merch present in the merchanise list we insert it in the data_merchandise divided for the total quantity of merchandise
            counter = 0
            partial_count = 0
            for merch in merchandise[city]:
                quantity = int((merchandise[city][merch] / total) * data_merchandise[city]['length'])
                partial_count += quantity
                data_merchandise[city][merch] = quantity
                # if there is a difference between the quantity inserted and the length we add/remove the quantity
                if counter == len(merchandise[city]) - 1 and partial_count != data_merchandise[city]['length']:
                    merchandise[city][merch] += (data_merchandise[city]['length'] - partial_count)
                counter += 1
    
def add_merch(data_merchandise: dict, merchandise: dict, city: str):
    '''
    function to insert the merch in the new route
    
    input:
        - data_merchandise, dict: dictionary in which there are stored the information to fill the new route merch
        - merchandise, dict: dict in which we need to store the new merch
        - city in which we are working
    '''
    # we need to calculate the total quantity of merch to have for the city in the new route
    total_merch = int(data_merchandise[city]['length'] / data_merchandise[city]['counter'])
    
    # we need to calculate the total quantity that the city now have
    total = 0
    for merch in data_merchandise[city]:
        if merch != 'length' and merch != 'counter':
            total += data_merchandise[city][merch]
        
    # we insert the quantity of the merch as: (quantity of the merch * total quantity that we need in the new route) / total quantity we have now
    for merch in data_merchandise[city]:
        if merch != 'length' and merch != 'counter':
            merchandise[merch] = int((data_merchandise[city][merch] * total_merch)/ total)


def find_perfect_route_per_driver(actuals: dict, result_file: str, city_weight = 0.6876561616433419, merch_weight = 0.31234383835665813):
    output = open(result_file, 'w')
    output.write('[\n')
    index = 0
    mean_time = list()
    drivers = get_drivers(actuals)
    for driver in drivers:
        start_time = time()
        route = find_perfect_route(driver, actuals)
        end_time = time()
        mean_time.append(get_elapsed_time(start_time, end_time))
        print('time to find the perfect route for', driver, ':', end_time - start_time)
        driver_actuals = get_actual_to_driver(driver, actuals)
        compare_perfect_actuals(driver_actuals, route, city_weight, merch_weight)
        json_output = json.dumps(route)
        output.write(json_output)
        if index == len(drivers) - 1:
            output.write('\n')
        else:
            output.write(',\n')
        index += 1
    output.write(']')
    print('mean time to find the perfect route:', sum(mean_time) / len(mean_time))
    
    
def compare_perfect_actuals(actuals, perfect, city_weight: int, merch_weight: int, is_perfect: bool = True):
    '''
    to test
    calculate the similarity of the perfect route with the actuals
    '''
    sum = 0
    for actual in actuals:
        city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B = get_features(actual, perfect)
        merch, city = similarity(city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B)
        cosine = (city * (1 - city_weight)) + (merch * (1 - merch_weight))
        
        sum += cosine
        
        # print for the output.txt
        if is_perfect:
            print('driver:', perfect['driver'], 'actual id:', actual['id'], 'similarity:', cosine)
            print('city similarity:', city, 'merch similarity:', merch)
            print('len actual:', len(actual['route']))
            print('len perfect', len(perfect['route']))
            print()
    
    print('sum of similarities for', perfect['driver'], ':', sum, '\n')
        
def test_perfects(actuals, city_weight = 0.7196538657216474, merch_weight = 0.28034613427835264):
    index = random.randint(0, len(actuals))
    perfect = actuals[index]
    driver = perfect['driver']
    actual_drivers = get_actual_to_driver(driver, actuals)
    print('actual as perfect')
    compare_perfect_actuals(actual_drivers, perfect, city_weight, merch_weight, False)


if __name__ == "__main__":
    actual_file = 'data/small/actual_small_normal.json'
    actuals = get_route(actual_file)
    result_file = 'results/perfectRoute.json'
    
    find_perfect_route_per_driver(actuals, result_file)
    print('\n\n\n')
    test_perfects(actuals)