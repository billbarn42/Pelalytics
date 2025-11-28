# Pelalytics

A robust Peloton Power Zone class scraper that extracts class metadata including difficulty ratings, instructor names, and dates. Built with Selenium for reliable browser automation and data extraction.

## Features

- 🔍 **Filter-based scraping** - Uses Peloton's native filters (no search limitations)
- 📅 **Date range filtering** - Extract classes from specific time periods
- 🚀 **Headless mode** - Fast, background scraping without browser UI
- 💾 **SQLite database** - Automatic deduplication and upsert logic
- 🎯 **Smart scrolling** - Automatically loads more classes as needed
- ⚡ **Intelligent skipping** - Fast-forwards through classes outside date range
- 📊 **Complete metadata** - Title, instructor, duration, difficulty rating, date, URL

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your Peloton credentials:

```
PELOTON_EMAIL=your_email@example.com
PELOTON_PASSWORD=your_password
```

### 3. Run the Scraper

```bash
# Scrape specific date range (recommended)
python refresh_cache.py --start-date 2025-11-01 --end-date 2025-11-30 --headless

# Scrape with default limit
python refresh_cache.py --max-classes 10

# Scrape without headless (see browser)
python refresh_cache.py --start-date 2024-01-01 --end-date 2024-12-31
```

## Usage
### Plan generation
Use `generate_plan.py` to build a training plan CSV from a template in `input/`.

Key behavior:
- When a template row is `FTP Test`, the generator automatically inserts the matched `FTP Warm Up` on the same day, immediately before the test.
- Matched warmup selection: same instructor and same date as the test; falls back to ±1 day if needed.
- Template warmup rows are ignored (warmups are auto-managed).

Example:
```bash
source venv/bin/activate
python generate_plan.py --template input/8-week-A-template.csv --start-date 2025-11-28 --allow-fallback
```

### Command-Line Options

```bash
python refresh_cache.py [OPTIONS]

Options:
  --start-date YYYY-MM-DD    Filter classes from this date (inclusive)
  --end-date YYYY-MM-DD      Filter classes until this date (inclusive)
  --max-classes N            Maximum classes to scrape (default: 10 without dates, 10000 with dates)
  --headless                 Run in headless mode (faster, no browser UI)
```

### Examples

**Scrape all of 2024:**
```bash
python refresh_cache.py --start-date 2024-01-01 --end-date 2024-12-31 --headless
```

**Scrape last 3 months:**
```bash
python refresh_cache.py --start-date 2025-08-01 --end-date 2025-10-31 --headless
```

**Test with 5 classes:**
```bash
python refresh_cache.py --max-classes 5
```

## How It Works

1. **Authenticates** with your Peloton account
2. **Navigates** to cycling classes page
3. **Applies filter** for Power Zone classes
4. **Scrolls and loads** classes from newest to oldest
5. **Checks dates** on class tiles (without opening modals)
6. **Skips classes** outside your date range
7. **Extracts details** for in-range classes:
   - Opens class modal
   - Scrapes difficulty rating, instructor, duration
   - Saves to database
   - Closes modal
8. **Stops automatically** when past date range

### Smart Date Handling

- **Fast-forward:** Quickly scrolls past classes newer than end_date
- **Extract:** Opens and scrapes classes in your date range
- **Stop:** Exits after 10 consecutive classes before start_date

This makes date-range scraping extremely efficient!

## Database

Data is stored in `peloton_classes.db` (SQLite):

### Schema

```sql
CREATE TABLE classes (
    id TEXT PRIMARY KEY,              -- Peloton class ID
    title TEXT,                       -- "45 min Power Zone Classic Rock Ride"
    instructor TEXT,                  -- "Matt Wilpers"
    duration_minutes INTEGER,         -- 45
    difficulty_rating REAL,           -- 7.9
    class_type TEXT,                  -- "Power Zone"
    original_air_time TEXT,           -- "2025-11-25"
    url TEXT                          -- Full Peloton URL
)
```

### Query Database

```bash
# View all classes
sqlite3 peloton_classes.db "SELECT * FROM classes;"

# View specific columns
sqlite3 peloton_classes.db -header -column "SELECT title, instructor, difficulty_rating FROM classes;"

# Count classes by instructor
sqlite3 peloton_classes.db "SELECT instructor, COUNT(*) FROM classes GROUP BY instructor;"

# Find hardest classes
sqlite3 peloton_classes.db "SELECT title, difficulty_rating FROM classes ORDER BY difficulty_rating DESC LIMIT 10;"
```

## Troubleshooting

### Browser doesn't open in headless mode
That's expected! Use `--headless` flag for background operation. Remove it to see the browser.

### Script stops after 10 classes
Check your date range - the script stops when it passes your start_date. Adjust dates or remove date filters.

### "Element click intercepted" errors
The modal didn't close properly. The script has retry logic, but if it persists, try without `--headless`.

### Authentication fails
1. Verify credentials in `.env`
2. Make sure your Peloton account is active
3. Check for typos in email/password

### No classes found
1. Verify Power Zone filter is working (run without `--headless` to see)
2. Check date range is valid (end_date should be after start_date)
3. Ensure you have Power Zone classes in that time period

## Files

```
.
├── refresh_cache.py          # Main scraper script
├── peloton_classes.db        # SQLite database (created on first run)
├── requirements.txt          # Python dependencies
├── .env                      # Your credentials (not in git)
├── .env.example             # Template for credentials
├── .gitignore               # Excludes sensitive files
├── README.md                # This file
├── input/                   # Optional input files
├── output/                  # Optional output exports
└── legacy/                  # Old code (archived)
```

## Strategy for Complete History

Since Peloton has years of Power Zone classes, scrape in chunks:

```bash
# 2025
python refresh_cache.py --start-date 2025-01-01 --end-date 2025-12-31 --headless

# 2024
python refresh_cache.py --start-date 2024-01-01 --end-date 2024-12-31 --headless

# 2023 (also the default in batch_scrape.py)
python refresh_cache.py --start-date 2023-01-01 --end-date 2023-12-31 --headless

# Continue back as far as needed...
```

The database automatically handles duplicates, so re-running is safe!

## Security

- `.env` is in `.gitignore` - never committed
- Database (`*.db`) is in `.gitignore` - stays local
- Never hardcode credentials in scripts

## Future Enhancements

- Export to CSV
- Filter by instructor
- Track scraping progress
- Auto-resume on interruption
- Difficulty trend analysis
- Training program generator

## License

MIT License - see LICENSE file

## Acknowledgments

Built with Selenium and ChromeDriver for reliable web scraping.
