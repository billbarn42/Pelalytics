import requests

BASE_URL = "https://api.onepeloton.com/api/v2/ride/archived"

params = {
    "browse_category": "cycling",
    "content_format": "audio,video",
    "limit": 10,
    "page": 0,
    "sort_by": "original_air_time",
    "desc": "true",
    "duration": 45 * 60,  # 45 min
    "class_type_ids": "665395ff3abf4081bf315686227d1a51"  # Power Zone
}

try:
    print(f"Requesting: {BASE_URL}")
    print(f"Params: {params}")
    response = requests.get(BASE_URL, params=params)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response text: {response.text[:1000]}")  # Print first 1000 chars
    data = response.json()
    print(f"Found {len(data.get('data', []))} rides.")
    for ride in data.get('data', []):
        print(f"Title: {ride.get('title')}, ID: {ride.get('id')}")
except Exception as e:
    print(f"Error: {e}")
