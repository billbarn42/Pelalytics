# Pelalytics - Complete Summary

## What You Now Have

A complete Python-based system for extracting Peloton data and generating personalized FTP-building training programs.

### Three Core Modules

1. **`pelolytics.py`** - Data Extraction
   - Fetches all your Peloton workouts and metrics
   - Stores data in organized CSV files
   - Incremental syncing (fast updates)
   - Automatic duplicate detection

2. **`analysis.py`** - FTP Analysis & Programming
   - `FTPAnalyzer`: Track FTP progression, identify training zones
   - `TrainingProgramGenerator`: Create 6 or 8-week programs
   - Built-in periodization (base → build → peak → recovery)
   - Zone-based training guidance

3. **`config.py`** - Your Configuration
   - Add your Peloton username/password
   - Kept safe with `.gitignore`

### Key Files

| File | Purpose |
|------|---------|
| `pelolytics.py` | Main data extraction script |
| `analysis.py` | FTP analysis & program generation |
| `config.py` | Your Peloton credentials |
| `requirements.txt` | Python dependencies (updated) |
| `README.md` | Comprehensive documentation |
| `API_RESEARCH.md` | Technical API details |
| `IMPLEMENTATION_GUIDE.md` | Step-by-step usage guide |
| `output/` | Generated CSV data |
| `venv/` | Python virtual environment |
| `peloton_client_repo/` | Peloton API wrapper library |

---

## Your Two Goals - Implementation Status

### ✅ Goal 1: Extract All Detail on Rides to Analyze Trends & Performance

**What it does:**
- Fetches complete workout history from your Peloton account
- Extracts detailed metrics: cadence, resistance, output, heart rate, duration, calories
- Stores in organized CSV files ready for analysis
- Tracks data incrementally (only new data on future runs)

**Output files:**
- `output/workouts.csv` - Summary of all workouts with ride/instructor details
- `output/workout_metrics.csv` - Detailed performance metrics for analysis

**How to use:**
```bash
source venv/bin/activate
python pelolytics.py
```

**Next: Analyze the data**
- Load CSVs into Excel, Python, or visualization tools
- Create charts of output, cadence, duration trends
- Identify personal records and patterns
- Track progress over time

---

### ✅ Goal 2: Build 6-8 Week Programs with Increasing, Peaking & Reducing Intensity

**What it does:**
1. Analyzes your historical workout data
2. Estimates your current FTP (Functional Threshold Power)
3. Generates periodized training programs:
   - **Weeks 1-2**: Aerobic base building (easy, endurance focus)
   - **Weeks 3-4**: Threshold development (moderate intensity)
   - **Weeks 5-6**: Peak power (hard, VO2 max and anaerobic)
   - **Weeks 7-8**: Taper and testing (recovery + FTP retest)

**How to use:**
```python
from analysis import FTPAnalyzer, TrainingProgramGenerator
import pandas as pd

# Analyze your data
metrics = pd.read_csv('output/workout_metrics.csv')
analyzer = FTPAnalyzer(metrics)
current_ftp = analyzer.get_current_ftp()

# Generate program
generator = TrainingProgramGenerator(current_ftp, training_level='intermediate')
program = generator.generate_8_week_periodized(target_ftp_increase=8.0)

# Export to CSV
generator.export_program('output/training_program.csv')
```

**Features:**
- Smart zone-based training (Z1-Z5)
- Built-in periodization principles
- Weekly structure recommendations
- Recovery weeks included
- Testing weeks for validation

---

## Technology Stack

- **Language**: Python 3.x
- **Data**: Peloton unofficial API (via `peloton_client` library)
- **Data Processing**: `pandas` for CSV handling
- **HTTP**: `requests` library
- **Environment**: Virtual environment (`venv`)

---

## Quick Start

### 1. Verify Setup ✓
```bash
source venv/bin/activate
python --version  # Should be 3.x
pip list | grep pandas  # Should see pandas, requests
```

### 2. Add Credentials
```bash
# Edit config.py and add your Peloton login
PELOTON_USERNAME = "your_email@example.com"
PELOTON_PASSWORD = "your_password"
```

### 3. Extract Your Data
```bash
python pelolytics.py
```

### 4. Analyze & Generate Program
```python
from analysis import FTPAnalyzer, TrainingProgramGenerator
import pandas as pd

metrics = pd.read_csv('output/workout_metrics.csv')
analyzer = FTPAnalyzer(metrics)
current_ftp = analyzer.get_current_ftp()

generator = TrainingProgramGenerator(current_ftp)
program = generator.generate_8_week_periodized()
generator.export_program('output/my_training_program.csv')
```

---

## Data Available for Analysis

### From Workouts
- Workout ID, date, time, duration
- Fitness discipline (cycling, running, etc.)
- Class title and description
- Instructor name and bio
- Status (completed, in-progress, etc.)

### From Metrics
- Total output (watts/joules)
- Cadence (RPM) - average and max
- Resistance (%) - average and max
- Heart rate (BPM) - average and max (if monitor available)
- Calories burned
- Distance
- Personal records achieved

---

## Training Zones Explained

Pelalytics automatically categorizes workouts by training zone:

- **Z1 (0-56% FTP)**: Active Recovery
  - Easy spinning, recovery work
  
- **Z2 (56-76% FTP)**: Endurance
  - Comfortable pace, builds aerobic base
  
- **Z3 (76-90% FTP)**: Tempo
  - "Comfortably hard", sustainable efforts
  
- **Z4 (90-105% FTP)**: Threshold
  - Hard efforts at/near FTP, lactate clearance work
  
- **Z5 (105%+ FTP)**: VO2 Max / Anaerobic
  - Very high intensity, maximum effort

---

## What's Different from Your Original Script

| Feature | Original | New |
|---------|----------|-----|
| API Library | Raw `requests` | `peloton_client` wrapper |
| Metrics | Workouts only | Workouts + detailed metrics |
| Analysis | None | FTP tracking & zones |
| Programs | None | 6 & 8-week periodized |
| Documentation | Basic README | Complete guide + examples |

---

## Files You Modified

- ✅ `pelolytics.py` - Complete rewrite for new API
- ✅ `requirements.txt` - Added peloton_client
- ✅ `README.md` - Full documentation update
- ✅ `API_RESEARCH.md` - Technical deep dive (NEW)
- ✅ `analysis.py` - Complete FTP module (NEW)
- ✅ `IMPLEMENTATION_GUIDE.md` - Usage guide (NEW)

---

## Credentials Security

⚠️ **IMPORTANT**: Keep your `config.py` safe!

- It contains your Peloton password
- It's in `.gitignore` to prevent accidental commits
- Never share or commit this file
- Only you should have access

---

## Troubleshooting

### Script won't authenticate
- Check credentials in `config.py`
- Verify Peloton account is active
- Peloton API restrictions may apply to some accounts
- Try running again in a few minutes

### No metrics data
- Ensure you have workouts on your Peloton account
- Different equipment may provide different fields
- Check column names in actual CSV files

### Analysis errors
- Run `pelolytics.py` first to create data
- Verify CSV files exist in `output/` folder
- Check that files have data (not just headers)

---

## Next Steps

1. **Immediate**:
   - Update `config.py` with your credentials
   - Run `python pelolytics.py` to extract data
   - Check `output/` folder for CSV files

2. **Short-term**:
   - Analyze the CSV data (Excel, Python, Tableau, etc.)
   - Create visualizations of your trends
   - Identify patterns and personal records

3. **Medium-term**:
   - Generate your first training program
   - Execute the 6 or 8-week program
   - Track actual workouts vs. recommendations

4. **Long-term**:
   - Re-analyze data to measure FTP gains
   - Generate new programs with higher FTP targets
   - Customize zone thresholds based on experience
   - Build multi-sport training plans

---

## Support Resources

| Resource | Content |
|----------|---------|
| `README.md` | Features, setup, usage examples |
| `IMPLEMENTATION_GUIDE.md` | Detailed step-by-step guide |
| `API_RESEARCH.md` | Technical API details |
| Code comments | Inline documentation |
| `peloton_client` repo | Library source code |

---

## Questions?

1. Check the relevant documentation file above
2. Review code comments in the Python files
3. Refer to examples in `IMPLEMENTATION_GUIDE.md`
4. Visit the `peloton_client` GitHub: https://github.com/kiera-dev/peloton_client

---

**You now have a complete system for:**
1. ✅ Extracting all your Peloton ride data
2. ✅ Analyzing trends and performance metrics
3. ✅ Generating personalized training programs
4. ✅ Tracking FTP progression
5. ✅ Implementing periodized training

**Ready to start?** Update `config.py` and run `python pelolytics.py`! 🚴‍♂️💪
