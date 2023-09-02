import requests
from config.base import env


# in progress
def get_geolocation(address: str, city: str, state: str):
    res = requests.get(
        f"https://maps.googleapis.com/maps/api/geocode/json?address={address},{city},{state}&key={env.GOOGLE_API_KEY}"
    )
