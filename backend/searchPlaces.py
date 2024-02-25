from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Type,List
from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
import requests
import os

class SearchNearbyPlacesSchema(BaseModel):
    place_type: str = Field(description="The type of place your looking for EX:(park,restaraunt,gym)")
    latitude: float = Field(description="The user's latitude")
    longitude:float = Field(description="The user's longitude")


class SearchNearbyPlacesTool(BaseTool):
    name = "SearchNearbyPlaces"
    description = "Finds a list of 10 nearby places with their name, address,and website_url"
    args_schema: Type[SearchNearbyPlacesSchema] = SearchNearbyPlacesSchema

    def _run(
        self,
        latitude,
        longitude,
        place_type,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool."""
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": os.getenv('GOOGLE_MAPS_API_KEY'),
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.types,places.websiteUri"
        }

        data = {
            "includedTypes": [place_type],
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "radius": 500.0
                },
            },
            "rankPreference": "DISTANCE"
        }

        response = requests.post(url, json=data, headers=headers)

        indexed_places = []

        for place in response.json()['places']:
            indexed_place = {
                'types': place['types'],
                'address': place['formattedAddress'],
                'url': place['websiteUri'],
                'name': place['displayName']['text']
            }
        indexed_places.append(indexed_place)
        return indexed_places


    async def _arun(
        self,
        latitude,
        longitude,
        place_type,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("search does not support async")