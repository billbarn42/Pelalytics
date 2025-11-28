#!/usr/bin/env python3
import requests
import json

API_BASE_URL = 'https://api.onepeloton.com'
API_HEADERS = {
    'Content-Type': 'application/json',
    'Peloton-Platform': 'web',
    'User-Agent': 'web',
}

username = 'bill@thirdstar.org'
password = 'Pedal:harder'

print(f"Attempting to authenticate with:")
print(f"  Username: {username}")
print(f"  Password: {'*' * len(password)}")
print()

request_parameters = {
    'username_or_email': username,
    'password': password,
}

try:
    response = requests.post(
        API_BASE_URL + '/auth/login',
        json=request_parameters,
        headers=API_HEADERS,
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
except Exception as e:
    print(f"Error: {e}")
