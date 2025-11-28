import pandas as pd
import os
import json
import sys
from datetime import datetime

# Add peloton_client repo to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'peloton_client_repo'))

from peloton_client import PelotonClient
from config import PELOTON_USERNAME, PELOTON_PASSWORD

def authenticate():
    """Authenticate with Peloton using peloton_client library"""
    try:
        client = PelotonClient(
            username=PELOTON_USERNAME,
            password=PELOTON_PASSWORD
        )
        print(f"🔐 Successfully authenticated as {PELOTON_USERNAME}")
        return client
    
    except ValueError as e:
        error_msg = str(e)
        print(f"❌ Authentication failed: {error_msg}")
        if "Session authorization failed" in error_msg or "Invalid credentials" in error_msg:
            print(f"   Please verify your Peloton username and password in config.py")
        raise SystemExit("Authentication failed. Check your credentials.")
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error during authentication: {error_msg}")
        raise SystemExit(f"Authentication error: {error_msg}")

def fetch_workouts(client):
    """Fetch all workouts using peloton_client with pagination"""
    try:
        print("🚴 Fetching all workouts...")
        workouts = client.fetch_workouts(fetch_all=True)
        return workouts
    
    except Exception as e:
        raise SystemExit(f"🚴 Error fetching workouts: {str(e)}")

def fetch_workout_metrics(client, workout_id):
    """Fetch detailed metrics for a specific workout"""
    try:
        metrics = client.fetch_workout_metrics(workout_id)
        return metrics
    except Exception as e:
        print(f"⚠️  Could not fetch metrics for workout {workout_id}: {str(e)}")
        return None

def load_existing_data(output_dir, data_file):
    """Load existing workout data if available"""
    filepath = os.path.join(output_dir, data_file)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return None

def save_metadata(output_dir, timestamp):
    """Save the last refresh timestamp"""
    metadata_file = os.path.join(output_dir, ".metadata.json")
    metadata = {"last_refresh": timestamp}
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f)

def load_metadata(output_dir):
    """Load the last refresh timestamp"""
    metadata_file = os.path.join(output_dir, ".metadata.json")
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            return metadata.get("last_refresh")
    return None

def flatten_workout_data(workout):
    """Flatten nested workout data into a single row"""
    flat = {}
    
    # Top-level workout fields
    for key, value in workout.items():
        if key == 'ride' and isinstance(value, dict):
            # Flatten ride data with prefix
            for ride_key, ride_value in value.items():
                if ride_key == 'instructor' and isinstance(ride_value, dict):
                    # Flatten instructor data
                    for inst_key, inst_value in ride_value.items():
                        flat[f'instructor.{inst_key}'] = inst_value
                else:
                    flat[f'ride.{ride_key}'] = ride_value
        elif isinstance(value, (dict, list)):
            # Skip complex nested structures (will be in separate metrics file)
            pass
        else:
            flat[key] = value
    
    return flat

def merge_workout_data(existing_df, new_df):
    """Merge new workouts with existing data, avoiding duplicates"""
    if existing_df is None:
        return new_df
    
    # Combine dataframes
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Remove duplicates based on workout ID
    if 'id' in combined_df.columns:
        combined_df = combined_df.drop_duplicates(subset=['id'], keep='last')
    
    # Sort by creation date if available
    if 'created_at' in combined_df.columns:
        combined_df = combined_df.sort_values('created_at', ascending=False)
    
    return combined_df.reset_index(drop=True)

def main():
    OUTPUT_DIR = "output"
    DATA_FILE = "workouts.csv"
    METRICS_FILE = "workout_metrics.csv"
    
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 Created output directory: {OUTPUT_DIR}")
    
    try:
        print("🔄 Starting Peloton data sync...")
        
        # Authenticate
        client = authenticate()
        
        # Fetch workouts
        raw_workouts = fetch_workouts(client)
        
        if not raw_workouts:
            print("✅ No workouts found")
            return
        
        print(f"✅ Fetched {len(raw_workouts)} workout(s)")
        
        # Flatten and process workout data
        flattened_workouts = [flatten_workout_data(w) for w in raw_workouts]
        new_workouts_df = pd.DataFrame(flattened_workouts)
        
        # Load existing data
        existing_df = load_existing_data(OUTPUT_DIR, DATA_FILE)
        
        # Merge data
        merged_df = merge_workout_data(existing_df, new_workouts_df)
        print(f"� Total workouts in database: {len(merged_df)}")
        
        # Save merged workouts data
        merged_df.to_csv(os.path.join(OUTPUT_DIR, DATA_FILE), index=False)
        print(f"💾 Saved {len(merged_df)} workouts to {os.path.join(OUTPUT_DIR, DATA_FILE)}")
        
        # Fetch and save detailed metrics for each workout
        print("📈 Fetching detailed metrics for workouts...")
        metrics_list = []
        
        for idx, workout in enumerate(raw_workouts, 1):
            workout_id = workout.get('id')
            if not workout_id:
                continue
            
            metrics = fetch_workout_metrics(client, workout_id)
            if metrics:
                # Add workout_id and basic info to metrics
                metrics_data = {
                    'workout_id': workout_id,
                    'created_at': workout.get('created_at'),
                    'fitness_discipline': workout.get('fitness_discipline'),
                }
                
                # Add performance metrics
                if isinstance(metrics, dict):
                    metrics_data.update(metrics)
                
                metrics_list.append(metrics_data)
            
            if idx % 5 == 0:
                print(f"  ⏳ Processed {idx}/{len(raw_workouts)} workouts...")
        
        if metrics_list:
            metrics_df = pd.DataFrame(metrics_list)
            
            # Load existing metrics
            existing_metrics = load_existing_data(OUTPUT_DIR, METRICS_FILE)
            if existing_metrics is not None:
                metrics_df = merge_workout_data(existing_metrics, metrics_df)
            
            metrics_df.to_csv(os.path.join(OUTPUT_DIR, METRICS_FILE), index=False)
            print(f"💾 Saved detailed metrics to {os.path.join(OUTPUT_DIR, METRICS_FILE)}")
        
        # Save refresh timestamp
        current_timestamp = datetime.now().isoformat()
        save_metadata(OUTPUT_DIR, current_timestamp)
        print(f"⏱️  Last refresh: {current_timestamp}")
        print("✨ Sync complete!")

    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")
        print("Troubleshooting steps:")
        print("1. Verify credentials in config.py")
        print("2. Check internet connection")
        print("3. Try again in 5 minutes")
        print("4. Check API_RESEARCH.md for more details")

if __name__ == "__main__":
    main()
