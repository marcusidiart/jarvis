"""JARVIS's tools: the things it can actually *do*.

Each tool has two parts:
  1. A plain Python function that does the work.
  2. A description (in TOOLS) that tells the AI what the tool is for
     and what inputs it takes. The AI reads this to decide when to call it.
"""

import os

import requests

PLACES_URL = "https://places.googleapis.com/v1/places:searchText"

# Only ask Google for the fields we use. Fewer fields = cheaper requests.
FIELDS = ",".join([
    "places.id",
    "places.displayName",
    "places.formattedAddress",
    "places.websiteUri",
    "places.nationalPhoneNumber",
    "places.rating",
    "places.userRatingCount",
    "places.regularOpeningHours",
    "places.photos",
])


def search_places(query: str) -> list[dict]:
    """Search Google Maps and return only businesses with no website listed."""
    response = requests.post(
        PLACES_URL,
        headers={
            "X-Goog-Api-Key": os.environ["GOOGLE_API_KEY"],
            "X-Goog-FieldMask": FIELDS,
        },
        json={"textQuery": query},
        timeout=20,
    )
    response.raise_for_status()
    places = response.json().get("places", [])

    results = []
    for place in places:
        if place.get("websiteUri"):
            continue  # already has a website, skip it
        results.append({
            "id": place["id"],
            "name": place["displayName"]["text"],
            "address": place.get("formattedAddress"),
            "phone": place.get("nationalPhoneNumber"),
            "rating": place.get("rating"),
            "review_count": place.get("userRatingCount"),
            "hours": place.get("regularOpeningHours", {}).get("weekdayDescriptions"),
            "photo_names": [p["name"] for p in place.get("photos", [])[:5]],
        })
    return results


# The "menu" of tools we show the AI.
TOOLS = [
    {
        "name": "search_places",
        "description": (
            "Search Google Maps for local businesses. Returns ONLY businesses "
            "that have no website listed, with their address, phone, rating, "
            "hours and photo references."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for, e.g. 'restaurants in Miami'",
                },
            },
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def run_tool(name: str, args: dict):
    """Run the tool the AI asked for and return its result."""
    if name == "search_places":
        return search_places(args["query"])
    raise ValueError(f"Unknown tool: {name}")
