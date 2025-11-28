# Pelalytics - Quick Reference

## Setup (One Time)

```bash
# Activate environment
source venv/bin/activate

# Edit credentials
nano config.py
# Update PELOTON_USERNAME and PELOTON_PASSWORD
```

## Extract Data

```bash
python pelolytics.py
```

Creates: `output/workouts.csv` and `output/workout_metrics.csv`

## Analyze & Generate Program

```python
from analysis import FTPAnalyzer, TrainingProgramGenerator
import pandas as pd

# Load and analyze
metrics = pd.read_csv('output/workout_metrics.csv')
analyzer = FTPAnalyzer(metrics)
current_ftp = analyzer.get_current_ftp()
print(f"Current FTP: {current_ftp:.0f}W")

# Generate 8-week program
generator = TrainingProgramGenerator(current_ftp)
program = generator.generate_8_week_periodized()
print(program)

# Export to CSV
generator.export_program('output/training_program.csv')
```

## Training Zones

| Zone | Intensity | Purpose |
|------|-----------|---------|
| Z1 | 0-56% FTP | Recovery |
| Z2 | 56-76% FTP | Endurance |
| Z3 | 76-90% FTP | Tempo |
| Z4 | 90-105% FTP | Threshold |
| Z5 | 105%+ FTP | VO2 Max |

## Common Tasks

### Get FTP Progression
```python
progression = analyzer.get_ftp_progression()
```

### Get Intensity Distribution (Last 12 Weeks)
```python
intensity = analyzer.get_intensity_distribution(weeks=12)
```

### Generate 6-Week Program (Instead of 8)
```python
program = generator.generate_6_week_build(target_ftp_increase=5.0)
```

### View Workout Data
```python
import pandas as pd
workouts = pd.read_csv('output/workouts.csv')
print(workouts.head())
```

### Find Personal Records
```python
workouts = pd.read_csv('output/workouts.csv')
prs = workouts[workouts['is_total_work_personal_record'] == True]
print(prs)
```

## File Structure

```
Pelalytics/
├── pelolytics.py           # Data extraction
├── analysis.py             # FTP analysis
├── config.py               # Your credentials
├── output/                 # Generated data
│   ├── workouts.csv
│   ├── workout_metrics.csv
│   └── training_program.csv (after you generate it)
└── README.md              # Full documentation
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Auth fails | Check config.py credentials |
| No data | Run pelolytics.py first |
| Missing columns | Different equipment = different fields |
| FTP is None | Need more workouts in history |

## Key Metrics

From `workout_metrics.csv`:
- `total_output` - Total watts
- `avg_cadence` - Average RPM
- `avg_resistance` - Bike resistance %
- `avg_heart_rate` - Average BPM (if available)
- `fitness_discipline` - Type of workout

## Program Structure

**8-Week Overview:**
- Weeks 1-2: Easy base building (Z1-Z2)
- Weeks 3-4: Threshold work (Z3-Z4)
- Weeks 5-6: VO2 max / peak (Z4-Z5)
- Week 7: Recovery (Z1-Z2)
- Week 8: FTP test + recovery

## More Info

- Full guide: `IMPLEMENTATION_GUIDE.md`
- Project summary: `PROJECT_SUMMARY.md`
- API details: `API_RESEARCH.md`
- Main docs: `README.md`

---

**Last Updated**: November 26, 2025
**Status**: Ready to use ✓
