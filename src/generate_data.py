import json

# Creating the dictionary structure
data = [
    {
        "id": "s5",
        "route": [
            {"from": "Rome", "to": "Milan", "merchandise": {"milk": 3, "pens": 10, "butter": 20}},
            {"from": "Milan", "to": "Verona", "merchandise": {"milk": 5, "honey": 9, "butter": 10, "tomatoes": 20}},
            {"from": "Verona", "to": "Venezia", "merchandise": {"butter": 7, "pens": 2, "tomatoes": 10}}
        ]
    },
    {
        "id": "s10",
        "route": [
            {"from": "Rome", "to": "Milan", "merchandise": {"milk": 2, "pens": 10, "butter": 20}},
            {"from": "Milan", "to": "Verona", "merchandise": {"milk": 5, "tomatoes": 24}},
            {"from": "Verona", "to": "Venezia", "merchandise": {"butter": 7, "bread": 2, "tomatoes": 10}}
        ]
    }
]

# Convert the dictionary to JSON
json_output = json.dumps(data, indent=4)

# Print the JSON output
print(json_output)