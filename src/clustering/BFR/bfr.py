import sys
sys.path.append('feature_extraction')
from feature_extraction import feature_extraction as fe

def BFR():
    city_indexes, cities_A, cities_B, merch_indexes, merch_A, merch_B = fe.get_features(fe.route_example, fe.route_example)
    print(city_indexes)
    print(cities_A)
    print(cities_B)
    print()
    print(merch_indexes)
    print(merch_A)
    print(merch_B)

if __name__ == "__main__":
    BFR()