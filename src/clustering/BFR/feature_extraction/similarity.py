
'''
we need to:
- find a measure of similarity between routes
- cluster the routes


find a measure of similarity
we can consider a route as a vector of 0s and 1s where
- 0 indicates that the city is not present in the route
- 1 indicates that the city is present in the route

in this way we can compare an actual route with a standard route and understand how many they are different
cosine distance?
p1 = 00111  p2 = 10011
p1p2 = 2 (two 1s in common) |p1| = |p2| = sqrt(3) (three 1s in the vector)
cos a = 2/3     a = 48 degree
'''

import json
import sys
import numpy as np
from numpy.linalg import norm
import sys
# sys.path.append('../feature_extraction')
# from feature_extraction import feature_extraction as fe
import feature_extraction as fe

# number_of_cities = int(sys.argv[1])

sroute = {
    "id": "a0",
    "driver": "D9",
    "sroute": "s5",
    "route": [
        {
            "from": "Itri",
            "to": "Lamporo",
            "merchandise": {
                "butter": 89,
                "honey": 76,
                "sparkling water": 46,
                "salad": 83,
                "spaghetti": 32,
                "water": 26
            }
        },
        {
            "from": "Lamporo",
            "to": "Fiorenzuola d'Arda",
            "merchandise": {
                "pasta": 5
            }
        },
        {
            "from": "Fiorenzuola d'Arda",
            "to": "Ferrazzano",
            "merchandise": {
                "tortel": 13,
                "pasta": 81
            }
        },
        {
            "from": "Ferrazzano",
            "to": "Tornaco",
            "merchandise": {
                "cookies": 22
            }
        },
        {
            "from": "Tornaco",
            "to": "Morro d'Alba",
            "merchandise": {
                "milk": 78,
                "tortel": 27
            }
        },
        {
            "from": "Morro d'Alba",
            "to": "Gambasca",
            "merchandise": {
                "honey": 80,
                "pizza": 59,
                "tomatoes": 24,
                "spaghetti": 63,
                "butter": 80,
                "salad": 10
            }
        },
        {
            "from": "Gambasca",
            "to": "Terruggia",
            "merchandise": {
                "butter": 78,
                "tomatoes": 39
            }
        },
        {
            "from": "Terruggia",
            "to": "San Gemini",
            "merchandise": {
                "bread": 45,
                "milk": 35,
                "spaghetti": 26,
                "butter": 94
            }
        },
        {
            "from": "San Gemini",
            "to": "Corte Palasio",
            "merchandise": {
                "pasta": 78,
                "honey": 95,
                "pizza": 13,
                "coca-cola": 59
            }
        },
        {
            "from": "Corte Palasio",
            "to": "Arcola",
            "merchandise": {
                "spaghetti": 94,
                "honey": 79,
                "pasta": 95,
                "tortel": 67,
                "salad": 60
            }
        },
        {
            "from": "Arcola",
            "to": "Chiusano d'Asti",
            "merchandise": {
                "spaghetti": 53,
                "tomatoes": 53,
                "salad": 13,
                "pasta": 10,
                "sparkling water": 74
            }
        },
        {
            "from": "Chiusano d'Asti",
            "to": "Sperone",
            "merchandise": {
                "milk": 48,
                "cookies": 84,
                "pasta": 13
            }
        },
        {
            "from": "Sperone",
            "to": "Baranzate",
            "merchandise": {
                "tomatoes": 26,
                "sparkling water": 26,
                "coca-cola": 32,
                "pasta": 12,
                "pens": 80,
                "bread": 81
            }
        },
        {
            "from": "Baranzate",
            "to": "Guasila",
            "merchandise": {
                "pens": 64,
                "salad": 33,
                "cookies": 24,
                "honey": 23,
                "butter": 80,
                "water": 13,
                "tortel": 48
            }
        },
        {
            "from": "Guasila",
            "to": "San Vito al Torre",
            "merchandise": {
                "butter": 100
            }
        },
        {
            "from": "San Vito al Torre",
            "to": "Valloriate",
            "merchandise": {
                "tortel": 54,
                "pizza": 99,
                "pasta": 45,
                "bread": 11,
                "milk": 60,
                "butter": 25,
                "spaghetti": 62,
                "honey": 37,
                "sparkling water": 11,
                "pens": 52
            }
        },
        {
            "from": "Valloriate",
            "to": "Intragna",
            "merchandise": {
                "butter": 41,
                "tortel": 63,
                "pizza": 6,
                "coca-cola": 16
            }
        },
        {
            "from": "Intragna",
            "to": "Graffignana",
            "merchandise": {
                "water": 46,
                "pens": 78,
                "tomatoes": 24,
                "spaghetti": 37
            }
        },
        {
            "from": "Graffignana",
            "to": "Montefalcone nel Sannio",
            "merchandise": {
                "pasta": 110,
                "salad": 16,
                "honey": 54,
                "water": 84,
                "pizza": 78
            }
        },
        {
            "from": "Montefalcone nel Sannio",
            "to": "Montechiaro d'Asti",
            "merchandise": {
                "spaghetti": 49,
                "tortel": 40,
                "milk": 51
            }
        },
        {
            "from": "Montechiaro d'Asti",
            "to": "Racconigi",
            "merchandise": {
                "pasta": 14,
                "honey": 43,
                "tortel": 40,
                "spaghetti": 21
            }
        },
        {
            "from": "Racconigi",
            "to": "Montieri",
            "merchandise": {
                "pasta": 87,
                "pizza": 60,
                "butter": 13,
                "coca-cola": 63,
                "spaghetti": 66
            }
        },
        {
            "from": "Montieri",
            "to": "Menconico",
            "merchandise": {
                "bread": 4,
                "honey": 35
            }
        },
        {
            "from": "Menconico",
            "to": "Dorzano",
            "merchandise": {
                "spaghetti": 79
            }
        },
        {
            "from": "Dorzano",
            "to": "Pianezze",
            "merchandise": {
                "butter": 16,
                "coca-cola": 25,
                "pasta": 92,
                "water": 57
            }
        },
        {
            "from": "Pianezze",
            "to": "Ravascletto",
            "merchandise": {
                "milk": 59,
                "bread": 71,
                "pens": 7,
                "coca-cola": 72,
                "tomatoes": 74,
                "spaghetti": 33,
                "sparkling water": 71,
                "honey": 79
            }
        },
        {
            "from": "Ravascletto",
            "to": "Albisola Superiore",
            "merchandise": {
                "pasta": 98,
                "water": 79,
                "pizza": 112
            }
        },
        {
            "from": "Albisola Superiore",
            "to": "Pretoro",
            "merchandise": {
                "water": 75,
                "tortel": 16,
                "milk": 60,
                "pasta": 72
            }
        },
        {
            "from": "Pretoro",
            "to": "Caposele",
            "merchandise": {
                "cookies": 96,
                "bread": 78,
                "spaghetti": 25,
                "salad": 32,
                "butter": 63,
                "tortel": 60,
                "honey": 28,
                "pasta": 22,
                "tomatoes": 61
            }
        },
        {
            "from": "Caposele",
            "to": "Volpara",
            "merchandise": {
                "tortel": 32,
                "milk": 42,
                "pasta": 53,
                "cookies": 14,
                "bread": 12,
                "water": 23,
                "pizza": 79,
                "salad": 86,
                "coca-cola": 98
            }
        },
        {
            "from": "Volpara",
            "to": "San Cataldo",
            "merchandise": {
                "butter": 24,
                "pizza": 88,
                "salad": 76,
                "pens": 98,
                "tortel": 11,
                "water": 14,
                "pasta": 64,
                "honey": 36
            }
        },
        {
            "from": "San Cataldo",
            "to": "Tricarico",
            "merchandise": {
                "pens": 15,
                "milk": 95,
                "sparkling water": 3,
                "water": 70,
                "pasta": 99,
                "pizza": 2,
                "salad": 32,
                "honey": 39,
                "spaghetti": 67,
                "tortel": 15
            }
        },
        {
            "from": "Tricarico",
            "to": "Mercallo",
            "merchandise": {
                "tortel": 66
            }
        },
        {
            "from": "Mercallo",
            "to": "Villette",
            "merchandise": {
                "salad": 55,
                "pizza": 77,
                "pens": 34,
                "tomatoes": 55
            }
        },
        {
            "from": "Villette",
            "to": "Terno d'Isola",
            "merchandise": {
                "honey": 17
            }
        },
        {
            "from": "Terno d'Isola",
            "to": "Castello d'Argile",
            "merchandise": {
                "spaghetti": 56
            }
        },
        {
            "from": "Castello d'Argile",
            "to": "Noale",
            "merchandise": {
                "pasta": 25,
                "coca-cola": 29
            }
        },
        {
            "from": "Noale",
            "to": "Rapolano Terme",
            "merchandise": {
                "water": 45
            }
        },
        {
            "from": "Rapolano Terme",
            "to": "Fabrica di Roma",
            "merchandise": {
                "pens": 61,
                "tomatoes": 14,
                "coca-cola": 8,
                "cookies": 44,
                "spaghetti": 91,
                "salad": 75,
                "milk": 50
            }
        },
        {
            "from": "Fabrica di Roma",
            "to": "Quartu Sant'Elena",
            "merchandise": {
                "tortel": 12,
                "sparkling water": 44,
                "cookies": 68
            }
        },
        {
            "from": "Quartu Sant'Elena",
            "to": "Villa Bartolomea",
            "merchandise": {
                "pasta": 40,
                "honey": 70,
                "sparkling water": 77
            }
        },
        {
            "from": "Villa Bartolomea",
            "to": "Domus de Maria",
            "merchandise": {
                "spaghetti": 85,
                "sparkling water": 92,
                "honey": 31
            }
        },
        {
            "from": "Domus de Maria",
            "to": "Montescano",
            "merchandise": {
                "water": 70,
                "butter": 6,
                "sparkling water": 41,
                "coca-cola": 19,
                "cookies": 31
            }
        },
        {
            "from": "Montescano",
            "to": "Civiasco",
            "merchandise": {
                "pizza": 89,
                "cookies": 79,
                "pens": 86
            }
        },
        {
            "from": "Civiasco",
            "to": "Valmorea",
            "merchandise": {
                "bread": 90,
                "tomatoes": 66,
                "butter": 77
            }
        },
        {
            "from": "Valmorea",
            "to": "Mazzarrone",
            "merchandise": {
                "pizza": 56
            }
        },
        {
            "from": "Mazzarrone",
            "to": "Proceno",
            "merchandise": {
                "water": 51
            }
        },
        {
            "from": "Proceno",
            "to": "Feletto",
            "merchandise": {
                "milk": 30,
                "pasta": 52
            }
        },
        {
            "from": "Feletto",
            "to": "Montevecchia",
            "merchandise": {
                "butter": 38,
                "tortel": 50,
                "bread": 3,
                "honey": 22
            }
        },
        {
            "from": "Montevecchia",
            "to": "Scandolara Ripa d'Oglio",
            "merchandise": {
                "butter": 15,
                "salad": 96,
                "coca-cola": 35,
                "spaghetti": 3,
                "cookies": 60,
                "tomatoes": 10,
                "pasta": 29,
                "milk": 24
            }
        },
        {
            "from": "Scandolara Ripa d'Oglio",
            "to": "Dosso del Liro",
            "merchandise": {
                "salad": 34,
                "pasta": 78,
                "water": 64,
                "milk": 63,
                "butter": 87
            }
        },
        {
            "from": "Dosso del Liro",
            "to": "Ollolai",
            "merchandise": {
                "sparkling water": 102,
                "milk": 90
            }
        },
        {
            "from": "Ollolai",
            "to": "Capriate San Gervasio",
            "merchandise": {
                "cookies": 77,
                "honey": 9,
                "pizza": 29
            }
        },
        {
            "from": "Capriate San Gervasio",
            "to": "Bozzole",
            "merchandise": {
                "pasta": 91,
                "pizza": 54,
                "milk": 17
            }
        },
        {
            "from": "Bozzole",
            "to": "Chiaravalle",
            "merchandise": {
                "salad": 43
            }
        },
        {
            "from": "Chiaravalle",
            "to": "Scagnello",
            "merchandise": {
                "honey": 86,
                "pens": 11,
                "pizza": 13,
                "coca-cola": 11,
                "tomatoes": 1,
                "spaghetti": 18
            }
        },
        {
            "from": "Scagnello",
            "to": "Savignano Irpino",
            "merchandise": {
                "pasta": 62
            }
        }
    ]
}

aroute = {
    "id": "a2",
    "driver": "D6",
    "sroute": "s5",
    "route": [
        {
            "from": "Arta Terme",
            "to": "Fiorenzuola d'Arda",
            "merchandise": {
                "spaghetti": 93
            }
        },
        {
            "from": "Fiorenzuola d'Arda",
            "to": "Fontanile",
            "merchandise": {
                "tortel": 13,
                "bread": 68,
                "cookies": 25,
                "pasta": 81
            }
        },
        {
            "from": "Fontanile",
            "to": "Sumirago",
            "merchandise": {
                "honey": 64,
                "coca-cola": 80,
                "cookies": 22
            }
        },
        {
            "from": "Sumirago",
            "to": "Gambasca",
            "merchandise": {
                "pizza": 64,
                "tortel": 50
            }
        },
        {
            "from": "Gambasca",
            "to": "San Costanzo",
            "merchandise": {
                "butter": 79,
                "tomatoes": 35
            }
        },
        {
            "from": "San Costanzo",
            "to": "Terruggia",
            "merchandise": {
                "spaghetti": 19,
                "honey": 26,
                "tortel": 94,
                "butter": 3
            }
        },
        {
            "from": "Terruggia",
            "to": "Zumpano",
            "merchandise": {
                "bread": 43,
                "milk": 52,
                "tomatoes": 45,
                "spaghetti": 29,
                "butter": 94,
                "pizza": 20,
                "pens": 8
            }
        },
        {
            "from": "Zumpano",
            "to": "Marcellinara",
            "merchandise": {
                "pasta": 71,
                "spaghetti": 44,
                "bread": 77,
                "honey": 95,
                "milk": 7,
                "pizza": 14,
                "coca-cola": 68,
                "tortel": 91
            }
        },
        {
            "from": "Marcellinara",
            "to": "Corte Palasio",
            "merchandise": {
                "pens": 31,
                "honey": 91
            }
        },
        {
            "from": "Corte Palasio",
            "to": "Piuro",
            "merchandise": {
                "spaghetti": 90,
                "honey": 97,
                "pasta": 100,
                "tortel": 67,
                "salad": 60
            }
        },
        {
            "from": "Piuro",
            "to": "Arcola",
            "merchandise": {
                "pizza": 75,
                "cookies": 81
            }
        },
        {
            "from": "Arcola",
            "to": "Carpaneto Piacentino",
            "merchandise": {
                "spaghetti": 53,
                "tomatoes": 53,
                "salad": 13,
                "pasta": 10,
                "sparkling water": 74
            }
        },
        {
            "from": "Carpaneto Piacentino",
            "to": "Chiusano d'Asti",
            "merchandise": {
                "tomatoes": 99,
                "pizza": 15,
                "tortel": 43,
                "cookies": 73,
                "milk": 99
            }
        },
        {
            "from": "Chiusano d'Asti",
            "to": "Busto Arsizio",
            "merchandise": {
                "milk": 48,
                "cookies": 84,
                "pasta": 13
            }
        },
        {
            "from": "Busto Arsizio",
            "to": "Sperone",
            "merchandise": {
                "pizza": 94
            }
        },
        {
            "from": "Sperone",
            "to": "Baranzate",
            "merchandise": {
                "water": 53,
                "tomatoes": 26,
                "sparkling water": 26,
                "coca-cola": 61,
                "pizza": 50,
                "pasta": 10,
                "spaghetti": 54,
                "tortel": 6,
                "pens": 81,
                "bread": 100
            }
        },
        {
            "from": "Baranzate",
            "to": "Casola di Napoli",
            "merchandise": {
                "pens": 64,
                "salad": 33,
                "cookies": 24,
                "butter": 80,
                "tortel": 48
            }
        },
        {
            "from": "Casola di Napoli",
            "to": "Guasila",
            "merchandise": {
                "butter": 95,
                "sparkling water": 57,
                "tomatoes": 50,
                "cookies": 67
            }
        },
        {
            "from": "Guasila",
            "to": "San Nazzaro Sesia",
            "merchandise": {
                "spaghetti": 15,
                "pasta": 4,
                "butter": 100
            }
        },
        {
            "from": "San Nazzaro Sesia",
            "to": "Tadasuni",
            "merchandise": {
                "pizza": 71,
                "bread": 11,
                "milk": 60,
                "butter": 25,
                "spaghetti": 62,
                "honey": 37,
                "sparkling water": 11,
                "pens": 52
            }
        },
        {
            "from": "Tadasuni",
            "to": "Valloriate",
            "merchandise": {
                "sparkling water": 79,
                "cookies": 43,
                "spaghetti": 17,
                "water": 96,
                "honey": 47,
                "milk": 89
            }
        },
        {
            "from": "Valloriate",
            "to": "Anoia",
            "merchandise": {
                "butter": 38,
                "tortel": 61,
                "pizza": 6
            }
        },
        {
            "from": "Anoia",
            "to": "Intragna",
            "merchandise": {
                "water": 11,
                "sparkling water": 81,
                "pizza": 73,
                "butter": 37,
                "spaghetti": 82
            }
        },
        {
            "from": "Intragna",
            "to": "San Giovanni Teatino",
            "merchandise": {
                "water": 59,
                "tortel": 20,
                "pens": 89,
                "bread": 76,
                "tomatoes": 24,
                "cookies": 6,
                "spaghetti": 37,
                "pasta": 50,
                "pizza": 75
            }
        },
        {
            "from": "San Giovanni Teatino",
            "to": "Montefalcone nel Sannio",
            "merchandise": {
                "cookies": 91,
                "tomatoes": 81,
                "milk": 2,
                "sparkling water": 66,
                "pasta": 2
            }
        },
        {
            "from": "Montefalcone nel Sannio",
            "to": "Caloveto",
            "merchandise": {
                "cookies": 34,
                "spaghetti": 49,
                "coca-cola": 6,
                "tortel": 40,
                "tomatoes": 13,
                "milk": 51
            }
        },
        {
            "from": "Caloveto",
            "to": "Montechiaro d'Asti",
            "merchandise": {
                "salad": 31,
                "sparkling water": 57,
                "butter": 69,
                "cookies": 24,
                "water": 12,
                "bread": 69,
                "pizza": 3,
                "tomatoes": 77
            }
        },
        {
            "from": "Montechiaro d'Asti",
            "to": "Castel di Iudica",
            "merchandise": {
                "pasta": 13,
                "honey": 36,
                "milk": 48,
                "tortel": 40,
                "pens": 10,
                "bread": 52,
                "spaghetti": 21,
                "salad": 43
            }
        },
        {
            "from": "Castel di Iudica",
            "to": "Dorzano",
            "merchandise": {
                "coca-cola": 33,
                "pizza": 33
            }
        },
        {
            "from": "Dorzano",
            "to": "Brosso",
            "merchandise": {
                "butter": 15,
                "pasta": 126,
                "milk": 69
            }
        },
        {
            "from": "Brosso",
            "to": "Fara Novarese",
            "merchandise": {
                "milk": 59,
                "bread": 71,
                "pens": 7,
                "coca-cola": 72,
                "spaghetti": 39
            }
        },
        {
            "from": "Fara Novarese",
            "to": "Albisola Superiore",
            "merchandise": {
                "milk": 43,
                "bread": 54,
                "sparkling water": 69,
                "butter": 34,
                "cookies": 27,
                "coca-cola": 37,
                "water": 74,
                "honey": 22
            }
        },
        {
            "from": "Albisola Superiore",
            "to": "Mallare",
            "merchandise": {
                "water": 92,
                "tortel": 19,
                "coca-cola": 50,
                "milk": 26,
                "tomatoes": 1,
                "sparkling water": 95,
                "pizza": 87
            }
        },
        {
            "from": "Mallare",
            "to": "Statte",
            "merchandise": {
                "cookies": 96,
                "bread": 78,
                "spaghetti": 27,
                "salad": 26,
                "milk": 7,
                "butter": 63,
                "tortel": 60,
                "honey": 28,
                "pasta": 20,
                "tomatoes": 73
            }
        },
        {
            "from": "Statte",
            "to": "San Cataldo",
            "merchandise": {
                "milk": 97,
                "water": 87
            }
        },
        {
            "from": "San Cataldo",
            "to": "Cuvio",
            "merchandise": {
                "pens": 15,
                "milk": 95,
                "sparkling water": 3,
                "water": 70,
                "pasta": 99,
                "pizza": 2,
                "salad": 32,
                "honey": 39,
                "spaghetti": 67,
                "tortel": 15
            }
        },
        {
            "from": "Cuvio",
            "to": "Tricarico",
            "merchandise": {
                "coca-cola": 17,
                "sparkling water": 85,
                "butter": 48
            }
        },
        {
            "from": "Tricarico",
            "to": "Rosciano",
            "merchandise": {
                "spaghetti": 72,
                "tomatoes": 24,
                "tortel": 66,
                "bread": 67
            }
        },
        {
            "from": "Rosciano",
            "to": "Castello d'Argile",
            "merchandise": {
                "tomatoes": 25,
                "milk": 16,
                "tortel": 50,
                "pasta": 27
            }
        },
        {
            "from": "Castello d'Argile",
            "to": "Moretta",
            "merchandise": {
                "bread": 91,
                "pasta": 23,
                "honey": 63,
                "coca-cola": 38,
                "tortel": 35,
                "salad": 25
            }
        },
        {
            "from": "Moretta",
            "to": "Noale",
            "merchandise": {
                "pens": 69
            }
        },
        {
            "from": "Noale",
            "to": "Lugo di Vicenza",
            "merchandise": {
                "water": 45
            }
        },
        {
            "from": "Lugo di Vicenza",
            "to": "Rapolano Terme",
            "merchandise": {
                "water": 77,
                "spaghetti": 81,
                "tomatoes": 26,
                "sparkling water": 25,
                "pens": 35,
                "butter": 30,
                "cookies": 31,
                "tortel": 59,
                "bread": 42,
                "honey": 6,
                "salad": 12,
                "pizza": 58
            }
        },
        {
            "from": "Rapolano Terme",
            "to": "Posina",
            "merchandise": {
                "tomatoes": 14,
                "coca-cola": 8,
                "cookies": 46,
                "salad": 75,
                "sparkling water": 30,
                "butter": 58
            }
        },
        {
            "from": "Posina",
            "to": "Villa Bartolomea",
            "merchandise": {
                "bread": 69,
                "water": 27,
                "spaghetti": 16,
                "butter": 5,
                "salad": 2,
                "honey": 82,
                "pizza": 36,
                "tomatoes": 69,
                "sparkling water": 69
            }
        },
        {
            "from": "Villa Bartolomea",
            "to": "Carate Brianza",
            "merchandise": {
                "spaghetti": 85,
                "sparkling water": 95,
                "tomatoes": 11
            }
        },
        {
            "from": "Carate Brianza",
            "to": "Domus de Maria",
            "merchandise": {
                "cookies": 2,
                "water": 46,
                "milk": 14,
                "butter": 21
            }
        },
        {
            "from": "Domus de Maria",
            "to": "Reggio nell'Emilia",
            "merchandise": {
                "salad": 49,
                "honey": 96,
                "water": 78,
                "butter": 6,
                "pasta": 90,
                "sparkling water": 42,
                "coca-cola": 25
            }
        },
        {
            "from": "Reggio nell'Emilia",
            "to": "Montescano",
            "merchandise": {
                "milk": 68,
                "pizza": 17,
                "cookies": 67,
                "pens": 65,
                "tomatoes": 30,
                "coca-cola": 53,
                "sparkling water": 35,
                "water": 57
            }
        },
        {
            "from": "Montescano",
            "to": "Fiumedinisi",
            "merchandise": {
                "pizza": 89,
                "cookies": 82,
                "pens": 86
            }
        },
        {
            "from": "Fiumedinisi",
            "to": "Civiasco",
            "merchandise": {
                "honey": 88,
                "pens": 58,
                "pizza": 89,
                "sparkling water": 19,
                "pasta": 90,
                "bread": 61,
                "cookies": 28
            }
        },
        {
            "from": "Civiasco",
            "to": "Gavirate",
            "merchandise": {
                "bread": 90,
                "tomatoes": 66,
                "butter": 77
            }
        },
        {
            "from": "Gavirate",
            "to": "Valmorea",
            "merchandise": {
                "tortel": 66,
                "pens": 5,
                "butter": 48,
                "honey": 34,
                "tomatoes": 94,
                "spaghetti": 21,
                "bread": 54
            }
        },
        {
            "from": "Valmorea",
            "to": "Alessano",
            "merchandise": {
                "pizza": 56
            }
        },
        {
            "from": "Alessano",
            "to": "Mazzarrone",
            "merchandise": {
                "salad": 4,
                "coca-cola": 38,
                "pizza": 38,
                "butter": 97,
                "cookies": 3,
                "pasta": 87,
                "honey": 5,
                "spaghetti": 71,
                "sparkling water": 20,
                "pens": 14
            }
        },
        {
            "from": "Mazzarrone",
            "to": "Trezzano sul Naviglio",
            "merchandise": {
                "water": 51,
                "tortel": 16
            }
        },
        {
            "from": "Trezzano sul Naviglio",
            "to": "Candelo",
            "merchandise": {
                "salad": 18,
                "milk": 88,
                "pasta": 52
            }
        },
        {
            "from": "Candelo",
            "to": "Castelnuovo di Val di Cecina",
            "merchandise": {
                "butter": 49,
                "tortel": 50,
                "bread": 3,
                "pasta": 36,
                "cookies": 85,
                "coca-cola": 90,
                "honey": 22,
                "spaghetti": 19,
                "water": 85
            }
        },
        {
            "from": "Castelnuovo di Val di Cecina",
            "to": "Santa Lucia di Piave",
            "merchandise": {
                "butter": 16,
                "coca-cola": 36,
                "cookies": 59,
                "tomatoes": 10,
                "pasta": 29,
                "milk": 28
            }
        },
        {
            "from": "Santa Lucia di Piave",
            "to": "Scandolara Ripa d'Oglio",
            "merchandise": {
                "pizza": 39,
                "salad": 79,
                "butter": 57,
                "coca-cola": 97,
                "tomatoes": 75
            }
        },
        {
            "from": "Scandolara Ripa d'Oglio",
            "to": "Ururi",
            "merchandise": {
                "salad": 34,
                "pasta": 78,
                "water": 64,
                "milk": 63,
                "butter": 87
            }
        },
        {
            "from": "Ururi",
            "to": "Ugento",
            "merchandise": {
                "honey": 9,
                "spaghetti": 69
            }
        },
        {
            "from": "Ugento",
            "to": "Bozzole",
            "merchandise": {
                "bread": 20,
                "coca-cola": 97,
                "sparkling water": 73,
                "tortel": 88,
                "cookies": 73,
                "pens": 95,
                "pasta": 48,
                "tomatoes": 3,
                "pizza": 60,
                "spaghetti": 45
            }
        },
        {
            "from": "Bozzole",
            "to": "Costa Vescovato",
            "merchandise": {
                "water": 12,
                "honey": 50,
                "pasta": 24,
                "salad": 52,
                "tortel": 97
            }
        },
        {
            "from": "Costa Vescovato",
            "to": "Chiaravalle",
            "merchandise": {
                "water": 22,
                "milk": 80,
                "spaghetti": 7,
                "salad": 59,
                "cookies": 30,
                "sparkling water": 2,
                "pizza": 33,
                "bread": 61
            }
        },
        {
            "from": "Chiaravalle",
            "to": "Pramollo",
            "merchandise": {
                "honey": 86,
                "pens": 11,
                "pizza": 13,
                "coca-cola": 11,
                "tomatoes": 1,
                "spaghetti": 18
            }
        },
        {
            "from": "Pramollo",
            "to": "Scagnello",
            "merchandise": {
                "pens": 41,
                "tomatoes": 93,
                "cookies": 47,
                "tortel": 37
            }
        },
        {
            "from": "Scagnello",
            "to": "Cimbergo",
            "merchandise": {
                "pasta": 62,
                "spaghetti": 41,
                "butter": 36
            }
        },
        {
            "from": "Cimbergo",
            "to": "Solarolo Rainerio",
            "merchandise": {
                "coca-cola": 94,
                "salad": 48,
                "water": 7,
                "bread": 62
            }
        }
    ]
}

with open("data/merchandise/merchandise_small.json") as merch_file:
    merchandise_global = json.load(merch_file)

def get_cities(number_of_cities: int) -> list:
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

# cities = get_cities(number_of_cities)
cities = []

def get_standard(standard_id: str):
    '''get the standard routes'''
    with open("data/standard3.json") as json_file:
        standard_routes = json.load(json_file)
    for route in standard_routes:
        if route["id"] == standard_id:
            return route
    return []

def get_actual():
    '''get the actual routes'''
    with open("data/actual_preference.json") as json_file:
        actual_routes = json.load(json_file)
    return actual_routes

'''
get actual
get standard related to the actual
convert the actual into a vector
convert the standard into a vector
'''

def create_vector_cities(route: list) -> set:
    cities_route: set = set()
    for trip in route:
        cities_route.add(trip['from'])
        cities_route.add(trip['to'])
    return cities_route

def create_vector_merch(route: list) -> dict:
    merch_route: dict = dict()
    for trip in route:
        merch_route[trip['to']] = trip['merchandise']
    return merch_route

def create_similarity_vector(route: dict) -> list:
    if isinstance(route, dict):
        route_vector: set = create_vector_cities(route['route'])
        similarity_vector: list = []
        for city in cities:
            similarity_vector.append(1) if city in route_vector else similarity_vector.append(0)
        return similarity_vector
    else:
        return []
    
def cosine_similarity(standard_route, actual_route):
    '''
    input:
        routeA : dict
        routeB : dict
    output:
        cosine : the cosine similarity between route A and route B
    '''
    standard_similarity_vector = create_similarity_vector(standard_route)
    actual_similarity_vector = create_similarity_vector(actual_route)
    A = np.array(standard_similarity_vector)
    B = np.array(actual_similarity_vector)
    cosine = np.dot(A, B)/ (norm(A) * norm(B))
    return cosine

def similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch):
    '''
    input:
        - standard_route: standard route
        - actual_route: actual_route
    
    output:
        - similarity: similarity between route A and route B given the similarity of the cities and the list of merch
    
    reasoning:
        - if a city is in both the route we check whether the merch has been respected or the driver has changed his quantity
        - if a city is present only in the standard route than we multiply for a certain weight the error
        - if a city is present only in the actual route than we multiply for another weight the error
    '''
    # city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch, _, _ = fe.get_features(standard_route, actual_route)
    
    A = np.array(standard_cities)
    B = np.array(actual_cities)
    route_cosine = np.dot(A, B) / (norm(A) * norm(B))
    
    cosines = list()
    # print(np.array(standard_cities))
    # print(np.array(actual_cities))
    # print("=====")
    for index in range(len(standard_cities)):
        # if the city is not present in both routes we skip it
        if standard_cities[index] == 0 and actual_cities[index] == 0: continue

        # if the city is present in both the routes:
        # if the city count is different pair up the closest merch vectors, and pair the rest of the merch vectors with null vectors
        # if the city count is equal compute the cosine similarity pairwise between vectors
        
        # take all the vectors related to the city
        standard = search_city_vectors(standard_merch, merch_indexes, city_indexes[index])
        actual = search_city_vectors(actual_merch, merch_indexes, city_indexes[index])

        penalty = 1
        
        new_standard = []
        new_actual = []
        # normalize the vectors to have the same length, and for items at the same index to be the closest possible
        if len(standard) > len(actual):
            # driver missed some cities
            penalty = 0.5
            # sort the vectors by cosine similarity - put at the same indexes the closest vectors, pair the outliers with the null vector
            for i in range(len(actual)):
                max_cosine = 0
                max_index = 0
                for j in range(len(standard)):
                    A = np.array(standard[j])
                    B = np.array(actual[i])
                    cosine = np.dot(A, B)/ (norm(A) * norm(B))
                    if cosine > max_cosine:
                        max_cosine = cosine
                        max_index = j
                new_standard.append(standard[max_index])
                new_actual.append(actual[i])
                standard.pop(max_index)
            for i in range(len(standard)):
                new_standard.append(standard[i])
                new_actual.append(create_vector_for_absent_city(standard[i], merch_indexes, city_indexes[index]))
            standard = new_standard
            actual = new_actual
        elif len(actual) > len(standard):
            # driver added some cities
            penalty = 0.75
            # sort the vectors by cosine similarity - put at the same indexes the closest vectors, pair the outliers with the null vector
            for i in range(len(standard)):
                max_cosine = 0
                max_index = 0
                for j in range(len(actual)):
                    A = np.array(standard[i])
                    B = np.array(actual[j])
                    cosine = np.dot(A, B)/ (norm(A) * norm(B))
                    if cosine > max_cosine:
                        max_cosine = cosine
                        max_index = j
                new_standard.append(standard[i])
                new_actual.append(actual[max_index])
                actual.pop(max_index)
            for i in range(len(actual)):
                new_standard.append(create_vector_for_absent_city(actual[i], merch_indexes, city_indexes[index]))
                new_actual.append(actual[i])
            standard = new_standard
            actual = new_actual
        # print the full vectors using numpy array
        # print("city: ", city_indexes[index])
        # print(np.array(standard))
        # print("-----")
        # print(np.array(actual))
        # print("\n\n")
        # if the city count is equal pair up the closest merch vectors and compute the cosine similarity
        if len(standard) == len(actual):
            for i in range(len(standard)):
                A = np.array(standard[i])
                B = np.array(actual[i])
                cosine = np.dot(A, B)/ (norm(A) * norm(B))
                cosine = cosine * penalty
                cosines.append(cosine)


    cosine_mean = sum(cosines) / len(cosines)
    # print(cosine_mean)
    return cosine_mean, route_cosine

'''
if standard_cities[index] == 1:
            standard = search_city_vector(standard_merch, merch_indexes, city_indexes[index])
            # if the list is empty then the city is the starting point of the route
            if len(standard) == 0: continue
        if actual_cities[index] == 1:
            actual = search_city_vector(actual_merch, merch_indexes, city_indexes[index])
            # if the list is empty then the city is the starting point of the route
            if len(actual) == 0: continue
        if standard_cities[index] == 0:
            standard = np.array(create_vector_for_absent_city(actual, merch_indexes, city_indexes[index]))
        if actual_cities[index] == 0:
            actual = np.array(create_vector_for_absent_city(standard, merch_indexes, city_indexes[index]))
        A = np.array(standard)
        B = np.array(actual)
        cosine = np.dot(A, B) / (norm(A) * norm(B))
        if standard_cities[index] == 0:
            cosine = cosine * 0.75
        if actual_cities[index] == 0:
            cosine = cosine * 0.5
        cosines.append(cosine)
'''

def search_city_vectors(route: list, merch_index: list, city: str):
    '''
    function that searches the vectors of merch related to the city
    
    input:
        - route: list of merch with respective cities
        - merch_index: list of labels for the route list
        - city: city to search
        
    output:
        - vector: list(s) of merch quantity related to the city
    '''
    vectors = []
    for index in range(len(merch_index)):
        # print(merch_index[index], city)
        if merch_index[index] == city:
            # print(merch_index[index], city)

            for vector in route:
                if vector[index] == 1:
                    vectors.append(vector)
    return vectors

def create_vector_for_absent_city(other: list, merch_index: list, city : str):
    '''
    create a vector with only zeros for all the merch and a single 1 indicating the city
    
    input:
        - other: list of merch and cities refering to the other route (if we are analazing the actual the other is the standard)
        - merch_index: list of labels for the route list
        - city: city to search
        
    output:
        - vector: list of merch and cities
    '''
    vector = list()
    for index in range(len(other)):
        if merch_index[index] == city:
            vector.append(1)
        else:
            vector.append(0)
    return vector

if __name__ == "__main__":
    """ actual_routes = get_actual()
    for route in actual_routes:
        standard_route = get_standard(route['sroute'])
        actual_similarity = create_similarity_vector(route)
        standard_similarity = create_similarity_vector(standard_route)
        A = np.array(actual_similarity)
        B = np.array(standard_similarity)
        cosine = np.dot(A, B)/ (norm(A)*norm(B))
        print(route['id'], route['sroute'], cosine) """
    # actual_routes = get_actual()
    # actual_route = actual_routes[0]
    # actual_route_2 = actual_routes[1]
    # standard_route = get_standard(actual_route['sroute'])
    # merch_sim, city_sim = similarity(standard_route, actual_route)

    city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch, _, _ = fe.get_features(sroute, aroute)
    print(np.array(city_indexes))
    print("\n\n")
    print(np.array(merch_indexes))
    print("\n\n")
    print("\n\n")
    print(similarity(city_indexes, standard_cities, actual_cities, merch_indexes, standard_merch, actual_merch))

    # city_indexes, standard_cities, merch_indexes, standard_merch = fe.get_features_total([sroute, aroute])
    # print(np.array(city_indexes))
    # print("\n\n")
    # print(np.array(merch_indexes))
    # print("\n\n")
    # print("\n\n")
    # print(similarity(city_indexes, standard_cities[0], standard_cities[1], merch_indexes, standard_merch[0], standard_merch[1]))
