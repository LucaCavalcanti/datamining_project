import numpy as np
from numpy.linalg import norm
from sklearn.feature_extraction import DictVectorizer
from time import time

vec = DictVectorizer()

route_example = {
        "id": "a0",
        "driver": "A",
        "sroute": "s2",
        "route": [
            {
                "from": "Louisville",
                "to": "Adamstown",
                "merchandise": {
                    "pens": 98,
                    "butter": 7,
                    "tomatoes": 63,
                    "milk": 28,
                    "honey": 12
                }
            },
            {
                "from": "Adamstown",
                "to": "Gongzhuling",
                "merchandise": {
                    "tomatoes": 81,
                    "butter": 83
                }
            },
            {
                "from": "Gongzhuling",
                "to": "Lingcheng",
                "merchandise": {
                    "milk": 92,
                    "bread": 19
                }
            },
            {
                "from": "Lingcheng",
                "to": "Saint Petersburg",
                "merchandise": {
                    "bread": 84,
                    "butter": 18,
                    "pens": 42,
                    "milk": 79
                }
            },
            {
                "from": "Saint Petersburg",
                "to": "Jining",
                "merchandise": {
                    "milk": 56,
                    "bread": 34,
                    "tomatoes": 71
                }
            },
            {
                "from": "Jining",
                "to": "Kaiyuan",
                "merchandise": {
                    "bread": 12,
                    "honey": 27,
                    "butter": 48,
                    "tomatoes": 100,
                    "milk": 88,
                    "pens": 76,
                    "carrot": 23
                }
            },
            {
                "from": "Kaiyuan",
                "to": "Managua",
                "merchandise": {
                    "pens": 74,
                    "butter": 10,
                    "milk": 41,
                    "tomatoes": 74
                }
            }
        ]
    }

route_id1 = {
        "id": "a0",
        "driver": "D0",
        "sroute": "s83",
        "route": [
            {
                "from": "Fossano",
                "to": "Incisa Scapaccino",
                "merchandise": {
                    "sparkling water": 50,
                    "pens": 50,
                    "salad": 45,
                    "bread": 18
                }
            },
            {
                "from": "Incisa Scapaccino",
                "to": "Borgarello",
                "merchandise": {
                    "spaghetti": 21,
                    "sparkling water": 6
                }
            },
            {
                "from": "Borgarello",
                "to": "San Lorenzello",
                "merchandise": {
                    "milk": 10
                }
            },
            {
                "from": "San Lorenzello",
                "to": "Recco",
                "merchandise": {
                    "tomatoes": 44,
                    "sparkling water": 50,
                    "water": 22,
                    "honey": 18,
                    "salad": 7
                }
            },
            {
                "from": "Recco",
                "to": "Tolfa",
                "merchandise": {
                    "tomatoes": 10
                }
            },
            {
                "from": "Tolfa",
                "to": "Acerno",
                "merchandise": {
                    "salad": 50,
                    "cookies": 25,
                    "sparkling water": 50,
                    "water": 36,
                    "pens": 16,
                    "butter": 15,
                    "tomatoes": 46,
                    "bread": 10
                }
            }
        ]
    }

route_id3 = {
        "id": "s83",
        "route": [
            {
                "from": "Fossano",
                "to": "Vicoli",
                "merchandise": {
                    "sparkling water": 49,
                    "pens": 20
                }
            },
            {
                "from": "Vicoli",
                "to": "Incisa Scapaccino",
                "merchandise": {
                    "cookies": 14,
                    "pizza": 8
                }
            },
            {
                "from": "Incisa Scapaccino",
                "to": "Bussero",
                "merchandise": {
                    "spaghetti": 21,
                    "sparkling water": 6
                }
            },
            {
                "from": "Bussero",
                "to": "Borgarello",
                "merchandise": {
                    "pasta": 31
                }
            },
            {
                "from": "Borgarello",
                "to": "Paola",
                "merchandise": {
                    "milk": 10
                }
            },
            {
                "from": "Paola",
                "to": "San Lorenzello",
                "merchandise": {
                    "tomatoes": 29
                }
            },
            {
                "from": "San Lorenzello",
                "to": "Fluminimaggiore",
                "merchandise": {
                    "tomatoes": 44,
                    "sparkling water": 44,
                    "water": 22,
                    "honey": 18
                }
            },
            {
                "from": "Fluminimaggiore",
                "to": "Cerreto d'Esi",
                "merchandise": {
                    "salad": 44,
                    "cookies": 30,
                    "sparkling water": 36,
                    "water": 36,
                    "pens": 16,
                    "butter": 15,
                    "tomatoes": 46
                }
            },
            {
                "from": "Cerreto d'Esi",
                "to": "Acerno",
                "merchandise": {
                    "sparkling water": 39,
                    "butter": 27
                }
            }
        ]
    }

def get_features(routeA, routeB):
    '''
    input:
        routeA : dict, routeB : dict
    output:
        city_indexes : list[str] of cities from both the routes,
        cities_A : list[int] of cities in route A with respect to city_indexes (1 if is present, 0 otherwise),
        cities_B : list[int] of cities in route B with respect to city_indexes (1 if is present, 0 otherwise),
        merch_indexes : list[str] of the merch from both the routes,
        merch_A: list[int] of merch for each city in route A
        merch_B: list[int] of merch for each city in route B
    '''
    # start = time()
    cities = {"cities": []}
    cities = {"city": []}
    merchA = []

    cities2 = {"city": []}
    merchB = []

    cities["city"].append(routeA["route"][0]["from"])
    cities2["city"].append(routeB["route"][0]["from"])

    len_routeA = 0
    for entry in routeA["route"]:
        cities["city"].append(entry["to"])
        merch_dict = {"city": entry["to"]}
        for merch_entry in entry["merchandise"]:
            merch_dict[merch_entry] = entry["merchandise"][merch_entry]
        merchA.append(merch_dict)
        len_routeA += 1

    for entry in routeB["route"]:
        cities2["city"].append(entry["to"])
        merch_dict = {"city": entry["to"]}
        for merch_entry in entry["merchandise"]:
            merch_dict[merch_entry] = entry["merchandise"][merch_entry]
        merchB.append(merch_dict)

    # partial = time()
    # print("Partial time: ", partial - start)

    res = vec.fit_transform([cities, cities2]).toarray()
    cities_A = res[0]
    cities_B = res[1]
    city_indexes = vec.get_feature_names_out()

    res = vec.fit_transform(merchA + merchB).toarray()
    merch_A = res[:len_routeA]
    merch_B = res[len_routeA:]
    merch_indexes = vec.get_feature_names_out()

    # end = time()
    # print("Total time: ", end - start)

    return city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B

def get_features_total(routes):
    # start = time()
    cities_total = []
    merch_total = []
    len_total = []

    for routeA in routes:
        cities = {"cities": []}
        merch = []

        cities["cities"].append(routeA["route"][0]["from"])

        len_routeA = 0
        for entry in routeA["route"]:
            cities["cities"].append(entry["to"])
            merch_dict = {"cities": entry["to"]}
            for merch_entry in entry["merchandise"]:
                merch_dict[merch_entry] = entry["merchandise"][merch_entry]
            merch.append(merch_dict)
            len_routeA += 1
        
        cities_total.append(cities)
        merch_total += merch
        len_total.append(len_routeA)

    # partial = time()
    # print("Partial time: ", partial - start)

    cities_res = vec.fit_transform(cities_total).toarray()
    city_indexes = vec.get_feature_names_out()

    merch_transform = vec.fit_transform(merch_total).toarray()
    merch_indexes = vec.get_feature_names_out()

    merch_res = []
    for len in len_total:
        merch_res.append(merch_transform[:len])
        merch_transform = merch_transform[len:]

    # end = time()
    # print("Total time: ", end - start)

    return city_indexes, cities_res, merch_indexes, merch_res

if __name__ == "__main__":
    city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B, a, b = get_features(route_id1, route_id3)
    print(city_indexes)
    print(cities_A)
    print(cities_B)
    print()
    print(merch_indexes)
    print(merch_A)
    print()
    print(merch_B)