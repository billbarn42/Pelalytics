import pandas as pd
import requests
import random
import os
from datetime import datetime

# --- CONFIGURATION ---
BASE_URL = "https://api.onepeloton.com/api/v2/ride/archived"
INSTRUCTORS = {
    "Matt Wilpers": "304389e2bfe44830854e071e512aa2b4",
    "Denis Morton": "1e59e949a19341539214a4a13ea7ff01",
    "Christine D'Ercole": "5a19bfe66e644a2fa3e6387a91ebc5ce",
    "Ben Alldis": "7f3de5e78bb44d8591a0f77f760478c3",
    "Olivia Amato": "05735e106f0747d2a12132295c99e3ee"
}
CLASS_TYPES = {
    "Power Zone Endurance": "757939e97c384c2f9034e29803a60876",
    "Power Zone": "665395ff3abf4081bf315686227d1a51",
    "Power Zone Max": "9f9be953f07d41949520e749d5874d36",
    "Low Impact": None,  # Not a PZ class, will match by title
    "Rest": None,
    "FTP Test": None,
    "Ride": None
}

# --- FUNCTION TO SEARCH FOR CLASSES ---
def search_classes(row, limit=20):
    """
    Search Peloton API for a class matching the plan row.
    Returns a dict with class info or None if not found.
    """
    class_type = row['Type']
    duration = int(row['Duration_Min'])
    # Handle NaN or empty instructor preference
    # Ignore instructor preference, only filter by class type and duration
    params = {
        "browse_category": "cycling",
        "content_format": "audio,video",
        "limit": limit,
        "page": 0,
        "sort_by": "original_air_time",
        "desc": "true",
        "duration": duration * 60
    }
    if class_type in CLASS_TYPES and CLASS_TYPES[class_type]:
        params["class_type_ids"] = CLASS_TYPES[class_type]
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        rides = data.get('data', [])
        if not rides:
            return None
        ride = random.choice(rides)
        return {
            'Class Title': ride.get('title'),
            'Instructor': ride.get('instructor_id'),
            'Duration': duration,
            'Class Type': class_type,
            'Peloton URL': f"https://members.onepeloton.com/classes/cycling?modal=classDetailsModal&classId={ride.get('id')}"
        }
    except Exception as e:
        return None

# --- MAIN SCRIPT ---
def main():
    plan_path = os.path.join('input', '8-week-plan.csv')
    plan = pd.read_csv(plan_path)
    output_rows = []
    for idx, row in plan.iterrows():
        if row['Type'] in ['Rest', 'FTP Test', 'Ride'] or row['Duration_Min'] == 0:
            # For rest/test/celebration, just copy row
            output_rows.append({**row, 'Class Title': row['Type'], 'Peloton URL': ''})
            continue
        class_info = search_classes(row)
        if class_info:
            output_rows.append({**row, **class_info})
        else:
            output_rows.append({**row, 'Class Title': 'No match found', 'Peloton URL': ''})
    output_df = pd.DataFrame(output_rows)
    now = datetime.now().strftime('%Y%m%d-%H%M')
    out_path = os.path.join('output', f'8-week-program-{now}.csv')
    output_df.to_csv(out_path, index=False)
    print(f"Populated plan written to {out_path}")

if __name__ == "__main__":
    main()
