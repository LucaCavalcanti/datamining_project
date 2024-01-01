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

def get_features(routeA, routeB):
    start = time()
    cities = {"cities": []}
    merchA = []

    cities2 = {"cities": []}
    merchB = []

    cities["cities"].append(routeA["route"][0]["from"])
    cities2["cities"].append(routeB["route"][0]["from"])

    len_routeA = 0
    for entry in routeA["route"]:
        cities["cities"].append(entry["to"])
        merch_dict = {"city": entry["to"]}
        for merch_entry in entry["merchandise"]:
            merch_dict[merch_entry] = entry["merchandise"][merch_entry]
        merchA.append(merch_dict)
        len_routeA += 1

    for entry in routeB["route"]:
        cities2["cities"].append(entry["to"])
        merch_dict = {"city": entry["to"]}
        for merch_entry in entry["merchandise"]:
            merch_dict[merch_entry] = entry["merchandise"][merch_entry]
        merchB.append(merch_dict)

    partial = time()
    # print("Partial time: ", partial - start)

    res = vec.fit_transform([cities, cities2]).toarray()
    cities_A = res[0]
    cities_B = res[1]
    city_indexes = vec.get_feature_names_out()

    res = vec.fit_transform(merchA + merchB).toarray()
    merch_A = res[:len_routeA]
    merch_B = res[len_routeA:]
    merch_indexes = vec.get_feature_names_out()

    end = time()
    # print("Total time: ", end - start)

    return city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B, partial - start, end - partial

def get_features_total(routes):
    start = time()
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
            merch_dict = {"city": entry["to"]}
            for merch_entry in entry["merchandise"]:
                merch_dict[merch_entry] = entry["merchandise"][merch_entry]
            merch.append(merch_dict)
            len_routeA += 1
        
        cities_total.append(cities)
        merch_total += merch
        len_total.append(len_routeA)

    partial = time()
    # print("Partial time: ", partial - start)

    cities_res = vec.fit_transform(cities_total).toarray()
    city_indexes = vec.get_feature_names_out()

    merch_transform = vec.fit_transform(merch_total).toarray()
    merch_indexes = vec.get_feature_names_out()

    merch_res = []
    for len in len_total:
        merch_res.append(merch_transform[:len])
        merch_transform = merch_transform[len:]

    end = time()
    # print("Total time: ", end - start)

    return city_indexes, cities_res, merch_indexes, merch_res


if __name__ == "__main__":
    city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B, partial, end = get_features(route_example, route_example)
    print(city_indexes)
    print(cities_A)
    print(cities_B)
    print()
    print(merch_indexes)
    print(merch_A)
    print(merch_B)