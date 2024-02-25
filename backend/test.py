import requests
import os
from dotenv import load_dotenv

load_dotenv()


url = "https://places.googleapis.com/v1/places:searchNearby"
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": os.getenv('GOOGLE_MAPS_API_KEY'),
    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.types,places.websiteUri"
}

data = {
    "includedTypes": ["restaurant"],
    "maxResultCount": 10,
    "locationRestriction": {
        "circle": {
            "center": {
                "latitude": 37.7937,
                "longitude": -122.3965
            },
            "radius": 500.0
        }
    }
}

response = requests.post(url, json=data, headers=headers)


indexed_places = []

for place in response.json()['places']:
    indexed_place = {
        'types': place['types'],
        'formattedAddress': place['formattedAddress'],
        'websiteUri': place['websiteUri'],
        'displayName': place['displayName']['text']
    }
    indexed_places.append(indexed_place)

# Print or use the indexed information as needed
for indexed_place in indexed_places:
    print("Place Name:", indexed_place['displayName'])
    print("Types:", indexed_place['types'])
    print("Formatted Address:", indexed_place['formattedAddress'])
    print("Website URI:", indexed_place['websiteUri'])
    print("\n")