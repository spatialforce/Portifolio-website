"""Settings for the site selection map. Add a city by giving it a bounding box."""

CITIES = {
    "harare": {"name": "Harare metro", "bbox": (30.86, -18.12, 31.26, -17.66)},  # west, south, east, north
}

# What counts as each kind of business in OpenStreetMap
CATEGORIES = {
    "supermarket": {"label": "Supermarkets", "tags": [("shop", "supermarket")]},
    "pharmacy": {"label": "Pharmacies", "tags": [("amenity", "pharmacy"), ("shop", "chemist")]},
    "bank": {"label": "Banks", "tags": [("amenity", "bank")]},
    "fuel": {"label": "Fuel stations", "tags": [("amenity", "fuel")]},
}

# Typical car speeds in km/h by road type, a little below the limits to allow for traffic
SPEED = {
    "motorway": 80, "trunk": 65, "primary": 50, "secondary": 42, "tertiary": 36,
    "motorway_link": 45, "trunk_link": 40, "primary_link": 35, "secondary_link": 32, "tertiary_link": 30,
    "unclassified": 28, "residential": 24, "living_street": 10, "service": 14, "road": 24, "track": 12,
}

# Getting from home to the nearest mapped road, along tracks that are not mapped (km/h);
# the distance is the straight line times DETOUR
ACCESS_KMH = 12
DETOUR = 1.3

# Best new sites: how many to suggest, and the drive time that counts as "nearby" (minutes)
SUGGEST = 10
NEAR_MIN = 10
