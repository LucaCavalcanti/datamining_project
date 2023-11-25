import json
import random
import sys

num_cities = int(sys.argv[1])
num_drivers = int (sys.argv[2])

def generate_preferences():
    cities = generate_italian_cities(num_cities)
    preferences = []
    for city in cities:
        percentage = random.randint(0, 100)
        preferences.append({'city': city, 'percentage': percentage})
    return preferences

def generate_drivers(num_drivers):
    drivers = []

    for driver in range(num_drivers):
        driver_id = f"D{driver}"
        driver_preferences = generate_preferences()
        drivers.append({'driver': driver_id, 'preferences': driver_preferences})
    
    return drivers

def generate_italian_cities(number_of_cities):
    cities_file = open("data/cities/italian_cities.csv", "r")
    cities = []
    cities_file.readline()
    counter = 0
    for cities_file_line in cities_file.readlines():
        if counter == number_of_cities:
            break
        cities.append(cities_file_line.split(";")[5].replace('"',''))
        counter += 1
    return cities

if __name__ == "__main__":
    drivers = generate_drivers(num_drivers)

    json_output = json.dumps(drivers, indent=4)
    output = open("data/drivers.json", "w")
    output.write(json_output)