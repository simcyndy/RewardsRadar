# square_api/square_service.py

import requests
from square.client import Client
import os

SQUARE_API_URL = 'https://connect.squareup.com/v2/'  # Base URL for Square API
SQUARE_ACCESS_TOKEN = 'EAAAEFRpdoZZVxTj0VN4Kg04vRidG5qi7H3hQNScg-btwkSUIONwnMByJFZANUZp'  # Replace with your access token

headers = {
    'Square-Version': '2023-05-31',  # Replace with the current date
    'Authorization': f'Bearer {SQUARE_ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

client = Client(
    access_token='EAAAEFRpdoZZVxTj0VN4Kg04vRidG5qi7H3hQNScg-btwkSUIONwnMByJFZANUZp',
    environment='sandbox')

result = client.locations.list_locations()

if result.is_success():
    for location in result.body['locations']:
        print(f"{location['id']}: ", end="")
        print(f"{location['name']}, ", end="")
        print(f"{location['address']['address_line_1']}, ", end="")
        print(f"{location['address']['locality']}")

elif result.is_error():
    for error in result.errors:
        print(error['category'])
        print(error['code'])
        print(error['detail'])


def get_locations():
    response = requests.get(f'{SQUARE_API_URL}locations', headers=headers)
    return response.json()  # Convert the response to JSON