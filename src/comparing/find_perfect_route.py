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


actual_file = 'actual_small.json'
result_file = 'perfectRoute.json'

def get_actual():
    '''to test
    
    get the actual routes'''
    with open("data/small2/" + actual_file) as json_file:
        actual_routes = json.load(json_file)
    return actual_routes

actual_routes = get_actual()

def get_actual_to_driver(driver_id: int):
    '''
    get the actual routes associated to the given driver
    '''
    actuals = list()
    for route in actual_routes:
        if route['driver'] == driver_id:
            actuals.append(route)
    return actuals

def get_drivers():
    '''
    get the list of drivers
    '''
    drivers = set()
    for route in actual_routes:
        drivers.add(route['driver'])
    return drivers

drivers = get_drivers()

def find_perfect_route(driver_id: int):
    '''
    function to find the perfect route for a specific driver
    
    input:
        - driver_id: int
        
    output:
        - best_route: dict, the perfect route for the driver
    '''
    
    actuals = get_actual_to_driver(driver_id)
    
    cities = dict()
    merchandise = dict()
    
    total_length = 0
    print(len(actuals))
    for actual in actuals:
        total_length += 1
        add_city(actual['route'][0]['from'], cities)
        for trip in actual['route']:
            city = trip['to']
            add_city(city, cities)
            total_length += 1
            if city not in merchandise:
                merchandise[city] = dict()
            for merch in trip['merchandise']:
                if merch in merchandise:
                    merchandise[city][merch] += trip['merchandise'][merch]
                else:
                    merchandise[city][merch] = trip['merchandise'][merch]
    
    new_route_length = int(total_length / len(actuals))
    print('new: ', new_route_length)
    
    sorted_cities = dict(sorted(cities.items(), key=lambda item: item[1], reverse=True))
    
    output = open('results/' + result_file, 'w')
    output.write('[\n')
    
    
    # take the n cities in order to create the new route where n is the length calculate in new_route_length
    cities_to_insert = list()
    for city in sorted_cities:
        if (len(cities_to_insert) == new_route_length):
            break
        if (city in merchandise):
            cities_to_insert.append(city)
            
    print(cities_to_insert)
    
    for index in range(len(cities_to_insert) - 1):
        city = cities_to_insert[index]
        next_city = cities_to_insert[index + 1]
        length = sorted_cities[city]
        mean_merch = dict()
        for merch in merchandise[city]:
            mean_merch[merch] = int(merchandise[city][merch] / length)
        json_output = json.dumps({'from': city, 'to': next_city, 'merchandise': mean_merch})
        output.write(json_output)
        
        if index == len(cities_to_insert) - 2:
            output.write('\n')
        else:
            output.write(',\n')
    
    output.write(']')

'''
dict<string, dict>
{
    'milano': {
        'tomatoes': 10,
        ...
    }
}

'''

def add_city(city: str, cities: dict):
    if city in cities:
        cities[city] += 1
    else:
        cities[city] = 1

def find_perfect_route_per_driver():
    for driver in drivers:
        find_perfect_route(driver)
        break


if __name__ == "__main__":
    find_perfect_route_per_driver()