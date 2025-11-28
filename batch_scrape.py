#!/usr/bin/env python3
"""
Batch scraper for Peloton classes by month.
Breaks large date ranges into monthly chunks to avoid stale element issues.
"""

import subprocess
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def get_month_ranges(start_year, start_month, end_year, end_month):
    """
    Generate list of (start_date, end_date) tuples for each month in range.
    
    Args:
        start_year: Starting year (e.g., 2025)
        start_month: Starting month (1-12)
        end_year: Ending year (e.g., 2025)
        end_month: Ending month (1-12)
    
    Returns:
        List of tuples: [(start_date, end_date), ...]
    """
    ranges = []
    current = datetime(start_year, start_month, 1)
    end = datetime(end_year, end_month, 1)
    
    while current <= end:
        # First day of month
        start_date = current
        
        # Last day of month
        next_month = current + relativedelta(months=1)
        end_date = next_month - timedelta(days=1)
        
        ranges.append((
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        ))
        
        current = next_month
    
    return ranges

def run_scraper(start_date, end_date, headless=True):
    """
    Run refresh_cache.py for a specific date range.
    
    Args:
        start_date: Start date string (YYYY-MM-DD)
        end_date: End date string (YYYY-MM-DD)
        headless: Whether to run in headless mode
    
    Returns:
        True if successful, False otherwise
    """
    cmd = [
        sys.executable,  # Use same Python interpreter
        'refresh_cache.py',
        '--start-date', start_date,
        '--end-date', end_date
    ]
    
    if headless:
        cmd.append('--headless')
    
    print(f"\n{'='*60}")
    print(f"📅 Scraping: {start_date} to {end_date}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(cmd, check=True)
        print(f"\n✅ Successfully scraped {start_date} to {end_date}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed to scrape {start_date} to {end_date}")
        print(f"   Error code: {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
        raise

def main():
    """Run batch scraping for all of 2025"""
    
    # Determine current month for end range
    now = datetime.now()
    end_month = now.month if now.year == 2025 else 12
    
    print(f"🚀 Starting batch scrape: January 2025 - {datetime(2025, end_month, 1).strftime('%B %Y')}")
    print("   Running in headless mode for speed")
    print("   Database will automatically handle duplicates\n")
    
    # Generate monthly ranges for 2025 (Jan through current month)
    ranges = get_month_ranges(2025, 1, 2025, end_month)
    
    total = len(ranges)
    success = 0
    failed = []
    
    for i, (start, end) in enumerate(ranges, 1):
        print(f"\n[{i}/{total}] Processing {start} to {end}...")
        
        try:
            if run_scraper(start, end, headless=True):
                success += 1
            else:
                failed.append((start, end))
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Batch scraping interrupted by user")
            print(f"   Completed: {success}/{i}")
            print(f"   Remaining: {total - i}")
            sys.exit(130)
    
    # Summary
    print(f"\n\n{'='*60}")
    print(f"📊 BATCH SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Successful: {success}/{total}")
    
    if failed:
        print(f"❌ Failed: {len(failed)}/{total}")
        print("\nFailed months:")
        for start, end in failed:
            print(f"   - {start} to {end}")
        print("\nYou can re-run these manually:")
        for start, end in failed:
            print(f"   python refresh_cache.py --start-date {start} --end-date {end} --headless")
    else:
        print(f"🎉 All months scraped successfully!")
    
    print(f"\n💾 Check your database: sqlite3 peloton_classes.db")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBatch scraping cancelled by user.")
        sys.exit(130)
