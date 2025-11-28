# Pelalytics

A Python script that fetches, analyzes, and programs Peloton workout data. Extract your complete ride history, track FTP progression, and generate personalized 6-8 week training programs with built-in periodization.

## Overview

Pelalytics uses the **peloton_client** library to connect to your Peloton account and retrieve detailed workout data. It automatically:
- Fetches your complete workout history with rich metrics
- Extracts detailed performance data (cadence, resistance, output, heart rate)
- Tracks FTP progression over time
- Builds training programs with intelligent periodization
- Stores everything locally for analysis and trending

## Features

- **✅ Complete Data Extraction**: Full workout history with ride details, instructor info, and performance metrics
- **✅ Detailed Metrics**: Cadence, resistance, output, heart rate, duration, calories
- **✅ FTP Analysis**: Estimate FTP progression, calculate training zones, analyze intensity
- **✅ Program Generation**: Create 6-week or 8-week FTP-building programs with periodization
  - Aerobic base building
  - Threshold and tempo development
  - VO2 Max and anaerobic work
  - Recovery phases
  - Built-in testing weeks
- **✅ Data Persistence**: Incremental updates with automatic duplicate detection
- **✅ Metadata Tracking**: Timestamps for intelligent sync scheduling

## How It Works

### Part 1: Data Extraction
1. **Authenticate** with your Peloton account (uses `peloton_client` library)
2. **Fetch** all workouts with detailed metrics from your account
3. **Parse** metrics including power output, cadence, resistance, heart rate
4. **Merge** with existing data, avoiding duplicates
5. **Export** to organized CSV files

### Part 2: Analysis & Programming
1. **Analyze** historical data to estimate current FTP
2. **Track** FTP progression week-over-week
3. **Generate** personalized 6 or 8-week training programs
4. **Structure** programs with smart periodization:
   - **Weeks 1-2**: Aerobic base building (Z1-Z2)
   - **Weeks 3-4**: Threshold development (Z3-Z4)
   - **Weeks 5-6**: Peak power and VO2 max (Z4-Z5)
   - **Week 7-8**: Taper and testing

## Requirements

- Python 3.x
- `requests` - HTTP library for API calls
- `pandas` - Data manipulation and CSV export
- `peloton_client` - Peloton API wrapper (installed from GitHub)

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment

```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

Edit `config.py` with your Peloton login:

```python
PELOTON_USERNAME = "your_email@example.com"
PELOTON_PASSWORD = "your_password"
```

⚠️ **Security Note**: `config.py` is in `.gitignore` - never commit it to version control!

### 5. Run the Script

```bash
python pelolytics.py
```

## Output Structure

```
output/
├── workouts.csv              # All workouts with ride/instructor details
├── workout_metrics.csv       # Detailed metrics (cadence, output, HR, etc.)
└── .metadata.json            # Internal timestamp tracking
```

## Usage Examples

### Fetch All Workout Data

```bash
python pelolytics.py
```

Output:
- Fetches all workouts from your account
- Automatically merges with existing data
- Creates/updates CSV files in `output/` folder

### Analyze Data & Generate Training Program

```python
from analysis import FTPAnalyzer, TrainingProgramGenerator
import pandas as pd

# Load your metrics data
metrics_df = pd.read_csv('output/workout_metrics.csv')

# Analyze FTP progression
analyzer = FTPAnalyzer(metrics_df)
current_ftp = analyzer.get_current_ftp()
print(f"Current FTP: {current_ftp:.0f}W")

# Generate 8-week training program
generator = TrainingProgramGenerator(current_ftp, training_level='intermediate')
program = generator.generate_8_week_periodized(target_ftp_increase=8.0)
print(program)

# Export program to CSV
generator.export_program('output/training_program.csv')
```

## Data Available

### Workout Summary (`workouts.csv`)
- Workout ID, date/time, status
- Duration, fitness discipline (cycling, running, etc.)
- Total output (watts), distance, calories
- Instructor details (name, bio, specialties)
- Ride/class information

### Detailed Metrics (`workout_metrics.csv`)
- All fields from workouts.csv plus:
- Performance graph data:
  - Average/max cadence
  - Average/max resistance
  - Average/max output
  - Average/max heart rate (if available)
- Segment breakdowns
- Metric summaries

## Analysis Features

### FTP Tracking

```python
analyzer = FTPAnalyzer(metrics_df)

# Get FTP progression over time
ftp_history = analyzer.get_ftp_progression()
# Returns: DataFrame with weekly estimated FTP

# Get current FTP
current_ftp = analyzer.get_current_ftp()
# Returns: Float with estimated FTP

# Get recent intensity distribution
intensity = analyzer.get_intensity_distribution(weeks=12)
# Returns: DataFrame with training zone distribution
```

### Training Zones

Zones are defined as % of FTP:
- **Z1** (0-56%): Active Recovery
- **Z2** (56-76%): Endurance
- **Z3** (76-90%): Tempo
- **Z4** (90-105%): Threshold
- **Z5** (105%+): VO2 Max / Anaerobic

### Program Generation

**6-Week Build Program**:
```python
generator = TrainingProgramGenerator(estimated_ftp=200, training_level='intermediate')
program = generator.generate_6_week_build(target_ftp_increase=5.0)
```

**8-Week Periodized Program**:
```python
program = generator.generate_8_week_periodized(target_ftp_increase=8.0)
```

## Troubleshooting

### Authentication Fails
1. Verify credentials in `config.py` are correct
2. Ensure your Peloton account is active
3. Check your internet connection

### No Metrics Found
1. Make sure you have Peloton workouts on your account
2. Check that the API can access your data
3. Wait a few minutes and try again

### Missing Columns in CSV
1. Different Peloton equipment may provide different data
2. Some metrics (HR) require a compatible device
3. Check the actual column names in the CSV files

## Files

- `pelolytics.py` - Main data extraction script
- `analysis.py` - FTP analysis and program generation
- `config.py` - Credentials (add your Peloton login here)
- `requirements.txt` - Python dependencies
- `.gitignore` - Keeps sensitive data safe
- `output/` - Generated data and CSV exports
- `venv/` - Virtual environment
- `API_RESEARCH.md` - Technical API details and alternatives

## How Data Sync Works

**First Run**:
- Fetches all historical workouts
- Creates CSV files in `output/`
- Records timestamp for next sync

**Subsequent Runs**:
- Loads existing data from `output/`
- Only fetches new workouts
- Automatically merges new data with existing
- Updates timestamp

This incremental approach keeps syncs fast and bandwidth-efficient!

## Notes & Limitations

- **FTP Estimation**: Calculated from weekly average output. For precise FTP, take a formal 20-minute power test
- **Metrics Availability**: Some metrics (HR) require compatible Peloton equipment
- **API Dependency**: Uses unofficial/reverse-engineered Peloton API (not officially supported)
- **Data Privacy**: Keep `config.py` with credentials safe and never commit to version control

## Future Enhancements

- Automated program tracking and adjustment
- Visual dashboards and charts
- Integration with Strava/Garmin
- Historical trend analysis
- Smart rest day recommendations
- Instructor and ride filtering/analysis

## References

- [peloton_client GitHub](https://github.com/kiera-dev/peloton_client)
- [API Research Details](API_RESEARCH.md)
- Unofficial Peloton API Spec: https://app.swaggerhub.com/apis/DovOps/peloton-unofficial-api/0.2.3
