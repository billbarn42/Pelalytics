# Pelalytics - Complete Implementation Guide

## What's Been Done

I've completely refactored Pelalytics to support your two-part goal:

### ✅ Part 1: Complete Ride Data Extraction
- **New**: Uses `peloton_client` library (maintained, actively working)
- **New**: Fetches detailed metrics (cadence, resistance, output, heart rate)
- **New**: Creates separate `workout_metrics.csv` for performance analysis
- **Preserved**: Incremental update system (no duplicate fetches)
- **Preserved**: Output folder organization
- **Improved**: Better error handling and logging

### ✅ Part 2: FTP Analysis & Program Generation
- **New**: `analysis.py` module with two main classes:
  - `FTPAnalyzer`: Calculates FTP progression, training zones, intensity distribution
  - `TrainingProgramGenerator`: Creates 6-week or 8-week periodized training programs

### ✅ Part 3: Documentation
- **Updated**: Comprehensive README with examples
- **New**: API_RESEARCH.md with technical details
- **New**: This guide with setup and usage instructions

---

## File Structure

```
Pelalytics/
├── pelolytics.py              # Main data extraction script
├── analysis.py                # FTP analysis & program generation
├── config.py                  # Your Peloton credentials
├── requirements.txt           # Dependencies (updated with peloton_client)
├── README.md                  # Complete documentation
├── API_RESEARCH.md            # API details and alternatives
├── IMPLEMENTATION_GUIDE.md    # This file
├── peloton_client_repo/       # Cloned peloton_client library
├── output/                    # Generated data (created by script)
│   ├── workouts.csv
│   ├── workout_metrics.csv
│   └── .metadata.json
└── venv/                      # Virtual environment
```

---

## Getting Started

### 1. Verify Your Setup

Your environment is already set up with:
- ✅ Virtual environment (`venv/`)
- ✅ Dependencies installed (`requests`, `pandas`)
- ✅ `peloton_client` cloned locally
- ✅ Scripts updated and ready

### 2. Update Your Credentials

Edit `config.py`:
```python
PELOTON_USERNAME = "InnerSpinner"  # Or your actual username
PELOTON_PASSWORD = "Pedal:harder"   # Your actual Peloton password
```

⚠️ **Keep this file safe!** It's in `.gitignore` and should never be committed.

### 3. Run the Data Extraction

```bash
# Activate virtual environment
source venv/bin/activate

# Run the script
python pelolytics.py
```

**What happens:**
1. Authenticates with your Peloton account
2. Fetches all your workouts
3. Extracts detailed metrics for each
4. Creates two CSV files in `output/`:
   - `workouts.csv` - Summary data
   - `workout_metrics.csv` - Detailed performance metrics
5. Saves timestamp for next incremental update

---

## Using the Analysis Tools

Once you have data extracted, use the `analysis.py` module:

### Example 1: Track FTP Progression

```python
from analysis import FTPAnalyzer
import pandas as pd

# Load your metrics
metrics = pd.read_csv('output/workout_metrics.csv')

# Create analyzer
analyzer = FTPAnalyzer(metrics)

# Get current FTP estimate
current_ftp = analyzer.get_current_ftp()
print(f"Current FTP: {current_ftp:.0f}W")

# Get weekly progression
progression = analyzer.get_ftp_progression()
print(progression)
```

### Example 2: Generate 8-Week Training Program

```python
from analysis import TrainingProgramGenerator
import pandas as pd

# Load metrics and analyze
metrics = pd.read_csv('output/workout_metrics.csv')

# ... get current_ftp from analyzer ...

# Generate program
generator = TrainingProgramGenerator(
    current_ftp=current_ftp,
    training_level='intermediate'  # or 'beginner', 'advanced'
)

# Create 8-week periodized program
program = generator.generate_8_week_periodized(target_ftp_increase=8.0)

# View program
print(program)

# Save to CSV
generator.export_program('output/training_program_8week.csv')
```

### Example 3: Get Intensity Distribution

```python
# Get training breakdown for last 12 weeks
intensity = analyzer.get_intensity_distribution(weeks=12)
print(intensity)
```

---

## Available Data

### From `workouts.csv`

Each row represents one workout with:
- `id` - Unique workout ID
- `created_at` - Timestamp
- `fitness_discipline` - Type (cycling, running, etc.)
- `status` - Completion status
- `ride.title` - Class/ride name
- `ride.duration` - Class length
- `instructor.name` - Instructor name
- `instructor.profile_image_url` - Instructor avatar
- And many more fields...

### From `workout_metrics.csv`

Detailed performance metrics:
- `total_output` - Total work in watts
- `avg_cadence` - Average RPM
- `max_cadence` - Peak RPM
- `avg_resistance` - Average bike resistance
- `max_resistance` - Peak resistance
- `avg_heart_rate` - Average heart rate (if monitor available)
- `max_heart_rate` - Peak heart rate
- `total_calories` - Calories burned
- And more...

---

## Training Program Structure

### 6-Week Build Program

| Week | Phase | Focus | Zone | Intensity | Rides/Wk | Duration |
|------|-------|-------|------|-----------|----------|----------|
| 1-2 | Base | Endurance | Z2-Z3 | Moderate | 3 | 45 min |
| 3-4 | Build | Threshold | Z3-Z4 | Hard | 3 | 50 min |
| 5 | Peak | VO2 Max | Z4-Z5 | Very Hard | 3 | 45 min |
| 6 | Recovery | Test | Z1-Z2 + Test | Easy + Mod | 2 | 40 min |

### 8-Week Periodized Program

| Week | Phase | Focus | Zone | Intensity | Rides/Wk | Duration |
|------|-------|-------|------|-----------|----------|----------|
| 1-2 | Aerobic Base | Foundation | Z1-Z2 | Easy-Mod | 3 | 50 min |
| 3-4 | Threshold | FTP Ceiling | Z3-Z4 | Hard | 3 | 50 min |
| 5-6 | Peak Power | VO2 + Anaerobic | Z4-Z5 | Very Hard | 3 | 45 min |
| 7 | Taper | Recovery | Z1-Z2 | Easy | 2 | 35 min |
| 8 | Test | FTP Assessment | Moderate-Hard | Controlled | 2 | 50 min |

---

## Understanding FTP & Zones

**FTP (Functional Threshold Power)**: The maximum average power you can sustain for approximately 60 minutes.

### Training Zones (as % of FTP):

- **Z1 (0-56%)**: Active Recovery
  - Easy spinning, recovery rides
  - Improves blood flow without stress

- **Z2 (56-76%)**: Endurance
  - Steady-state aerobic work
  - Builds aerobic base and fat utilization

- **Z3 (76-90%)**: Tempo
  - Comfortably hard, sustainable efforts
  - Builds aerobic power

- **Z4 (90-105%)**: Threshold
  - Hard efforts at or near FTP
  - Improves lactate clearance

- **Z5 (105%+)**: VO2 Max / Anaerobic
  - Very hard intervals
  - Builds peak power and maximum aerobic capacity

---

## How to Use This for Your Two Goals

### Goal 1: Extract All Detail on Rides to Analyze Trends & Performance

✅ **Run `pelolytics.py`** to get:
- Complete workout history in `workouts.csv`
- Detailed metrics in `workout_metrics.csv`
- Ready for analysis, trending, personal records tracking

**Next Steps:**
- Load CSV files into Excel, Python, or visualization tools
- Create charts of:
  - Output progression over time
  - Average cadence/resistance trends
  - Duration patterns
  - Instructor preferences
  - Class type breakdowns

### Goal 2: Build 6-8 Week Programs with Increasing, Peaking, Reducing Intensity

✅ **Use `analysis.py`** to:
1. Analyze your historical data for current FTP
2. Generate periodized programs with:
   - Intelligent zone progression
   - Build → Peak → Recovery structure
   - Built-in FTP testing weeks
   - Specific duration and frequency recommendations

**Next Steps:**
```python
# Get current fitness level
analyzer = FTPAnalyzer(metrics)
current_ftp = analyzer.get_current_ftp()

# Generate your next program
generator = TrainingProgramGenerator(current_ftp)
program = generator.generate_8_week_periodized()

# Execute the program week-by-week
# Track your actual rides against recommendations
# Re-analyze in 8 weeks to see FTP gains!
```

---

## Troubleshooting

### "Authentication failed: Invalid credentials"
- Verify username/password in `config.py`
- Ensure your Peloton account is active
- Try resetting your Peloton password and updating `config.py`
- Wait a moment and try again (API rate limiting)

### "No power column found in metrics"
- Make sure you have Peloton workouts on your account
- Different equipment may provide different data fields
- Check actual column names in `workout_metrics.csv`

### "Module not found: peloton_client"
- Ensure `peloton_client_repo/` directory exists in your project root
- If not, run: `git clone https://github.com/kiera-dev/peloton_client.git peloton_client_repo`

### Analysis returns empty DataFrames
- Run `pelolytics.py` first to create CSV files
- Verify CSV files exist in `output/` folder
- Check that metrics file has data (not just headers)

---

## Next Advanced Steps

Once the basics are working:

1. **Create Visualizations**:
   ```python
   import matplotlib.pyplot as plt
   ftp_history = analyzer.get_ftp_progression()
   plt.plot(ftp_history['date'], ftp_history['estimated_ftp'])
   plt.show()
   ```

2. **Track Program Execution**:
   - Create CSV with actual rides vs. recommended workouts
   - Compare actual output to target zones
   - Measure progress week-to-week

3. **Smart Program Adjustments**:
   - If falling short, reduce intensity next week
   - If crushing it, increase target FTP gain
   - Auto-extend programs based on performance

4. **Multi-Sport Integration**:
   - Combine cycling + running + strength training
   - Adjust programs for cross-training

---

## Key Features Summary

| Feature | Status | Location |
|---------|--------|----------|
| Peloton data extraction | ✅ | `pelolytics.py` |
| Incremental syncing | ✅ | `pelolytics.py` |
| Detailed metrics | ✅ | `pelolytics.py` → `workout_metrics.csv` |
| FTP analysis | ✅ | `analysis.py` → `FTPAnalyzer` |
| Zone calculation | ✅ | `analysis.py` → `ZONES` |
| 6-week programs | ✅ | `analysis.py` → `generate_6_week_build()` |
| 8-week programs | ✅ | `analysis.py` → `generate_8_week_periodized()` |
| Program export | ✅ | `analysis.py` → `export_program()` |
| Intensity tracking | ✅ | `analysis.py` → `get_intensity_distribution()` |

---

## Important Notes

1. **FTP Estimation**: Calculated from historical data, but actual FTP requires a formal 20-minute test
2. **API Dependency**: Uses reverse-engineered Peloton API (not official)
3. **Data Privacy**: Keep `config.py` safe - it contains credentials
4. **Incremental Updates**: After first full sync, subsequent runs are much faster
5. **Customization**: All thresholds, zones, and phases are customizable in `analysis.py`

---

## Questions or Issues?

Check these resources:
1. `README.md` - Usage and feature overview
2. `API_RESEARCH.md` - Technical API details
3. Inline code comments in `pelolytics.py` and `analysis.py`
4. `peloton_client` library: https://github.com/kiera-dev/peloton_client

---

**Ready to get started? Run: `python pelolytics.py`** 🚴‍♂️💪
