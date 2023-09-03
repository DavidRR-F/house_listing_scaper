import requests
from config.base import env


# in progress
def get_geolocation(street, city, state, zip):
    url = env.GEOCODE_API
    payload = {
        "format": "json",
        "street": street,
        "city": city,
        "state": state,
        "postalcode": zip,
    }
    try:
        res = requests.get(url=url, params=payload)
        res = res.json()
        return res[0]["lat"], res[0]["lon"]
    except:
        return None, None
