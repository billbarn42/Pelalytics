# Peloton API Research & Alternatives

## Current Status
As of November 2025, the official Peloton authentication endpoint (`/auth/login`) is returning a **403 Forbidden** with the message: "Access forbidden. Endpoint no longer accepting requests."

This means Peloton has shut down public API access.

## Available Options

### Option 1: `peloton_client` Python Library (RECOMMENDED)
**Status**: ✅ **ACTIVELY MAINTAINED & WORKING** (Updated Feb 2024+, recent activity confirms it works)

- **GitHub**: https://github.com/kiera-dev/peloton_client
- **Key Points**:
  - Pure Python wrapper for Peloton unofficial API
  - Uses the `Peloton-Platform: web` header (critical workaround)
  - Actively maintained with recent updates
  - README confirms "Oh snap this still works" (as of latest update)
  - Includes all methods needed for your use case

**Available Methods**:
- `fetch_workouts(limit=10, fetch_all=True)` - Get all workout history
- `fetch_workout_metrics(workout_id)` - Performance graph data (cadence, resistance, output, heart rate)
- `fetch_ride(ride_id)` - Ride/class details
- `fetch_user_overview()` - Summary stats
- `fetch_user_achievements()` - Achievement data

**Setup**:
```python
from peloton_client import PelotonClient

client = PelotonClient(username="InnerSpinner", password="Pedal:harder")
workouts = client.fetch_workouts(fetch_all=True)
for workout in workouts:
    metrics = client.fetch_workout_metrics(workout['id'])
    # process metrics
```

---

### Option 2: `geudrik/peloton-client-library`
**Status**: ⚠️ **OLDER BUT FUNCTIONAL** (Last update Nov 2020, but similar architecture)

- **GitHub**: https://github.com/geudrik/peloton-client-library
- **Key Points**:
  - More comprehensive object-oriented design
  - Good documentation via API_DOCS.md
  - Older (2018-2020), but similar endpoints
  - Uses lazy loading to minimize API calls
  - MIT Licensed

---

### Option 3: Official Peloton API (if available)
**Status**: ❌ **NOT AVAILABLE**
- Peloton has not released an official public API
- All current options are reverse-engineered from the web app

---

## Why `peloton_client` is Recommended for Your Use Case

1. **Actively Maintained**: Recent GitHub activity confirms it works with current Peloton API
2. **Perfect for Your Goals**:
   - ✅ Extract detailed ride data with metrics (cadence, resistance, output, heart rate)
   - ✅ Get historical workout trends (needed for FTP analysis)
   - ✅ Fetch instructor/ride details
3. **Simple Integration**: Easy to drop into your existing Pelalytics script
4. **Critical Header**: Uses `Peloton-Platform: web` header that bypasses the auth endpoint block

---

## Important Note: The "web" Header Workaround

The key difference that makes `peloton_client` work:

```python
API_HEADERS = {
    'Content-Type': 'application/json',
    'Peloton-Platform': 'web',  # ← This is critical!
    'User-Agent': 'web',
}
```

Your original script wasn't using this header, which likely contributed to the authentication failure.

---

## Data Available for Your FTP Program Goal

With `peloton_client`, you can get:

**Per Workout**:
- Workout ID, date, duration
- Fitness discipline (cycling, running, etc.)
- Total output (watts)
- Distance, calories burned
- Average cadence, resistance
- Heart rate data (if monitor used)
- Personal records achieved

**Metrics Over Time**:
- Historical output by date (track FTP improvements)
- Cadence/resistance trends
- Duration trends
- Instructor preferences
- Ride type preferences

**For Program Building**:
- Extract "best" rides (high output, long duration)
- Analyze FTP progression
- Identify intensity patterns
- Build 6-8 week programs with periodization:
  - Build phase (steady increase)
  - Peak phase (max intensity)
  - Recovery phase (reduced intensity)

---

## Next Steps

1. **Install peloton_client**:
   ```bash
   pip install git+https://github.com/kiera-dev/peloton_client.git
   ```

2. **Replace authentication** in your Pelalytics script to use `PelotonClient` instead of raw requests

3. **Expand data extraction** to include metrics data

4. **Store additional fields** needed for FTP/program analysis

5. **Build program generator** once you have 3+ months of historical data

---

## References
- Peloton Client: https://github.com/kiera-dev/peloton_client
- API Docs (reverse-engineered): https://app.swaggerhub.com/apis/DovOps/peloton-unofficial-api/0.2.3
- Older but comprehensive docs: https://github.com/geudrik/peloton-client-library/blob/main/API_DOCS.md
