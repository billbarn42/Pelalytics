#!/usr/bin/env python3
"""Generate a structured training plan from a template CSV.

Reads a plan template (e.g. `input/8-week-plan.csv`) containing weekly rows:
Week,Phase,Day,Type,Duration_Min,Intensity_Min,Intensity_Max,Instructor_Preference,Notes

For each non-rest entry it queries the local SQLite database (`peloton_classes.db`) and selects
one random matching class by:
    - Matching Type via title keyword heuristics
    - Matching duration exactly first, with fallback to nearest within ±15 minutes
    - Difficulty rating within provided min/max, widening if no match (if --allow-fallback is set)
    - Respecting instructor preference list first, then any instructor
    - Avoiding duplicates within the generated plan

Always uses the full template (no week limiting) and considers ALL classes in the database
regardless of age to ensure broad historical variety.

Outputs a CSV: `output/training-plan-YYYYMMDD-HHMM.csv` with columns:
Week,Date,Phase,Day,Template_Type,Selected_Class_ID,Title,Instructor,Duration,Intensity_Min,Intensity_Max,Difficulty_Rating,URL,Notes

Usage examples:
    python generate_plan.py --template input/8-week-plan.csv --start-date 2025-12-01 --allow-fallback
    python generate_plan.py --allow-fallback

Arguments:
    --template       Path to template CSV (default: input/8-week-plan.csv)
    --start-date     ISO start date for Week 1 Day 1 (default: next Monday)
    --db-path        Path to SQLite DB (default: peloton_classes.db)
    --allow-fallback Broaden matching aggressively if no strict match

Exit prints summary of counts and any rows without matches.
"""

import argparse
import csv
import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DB = "peloton_classes.db"
KEYWORD_MAP = {
    # Template Type -> list of required substrings in title (case-insensitive)
    "Power Zone Endurance": ["Power Zone Endurance"],
    "Power Zone Max": ["Power Zone Max"],
    "Power Zone": ["Power Zone"],  # Will later exclude Endurance/Max if explicitly Power Zone
    "FTP Test": ["FTP Test"],
    "Low Impact": ["Low Impact"],
    "Ride": ["Ride"],  # Generic celebration ride
}

EXCLUDE_SUBSTRINGS_FOR_PURE_POWER_ZONE = ["Endurance", "Max"]

def next_monday(today=None):
    today = today or datetime.today()
    days_ahead = (0 - today.weekday() + 7) % 7  # 0=Monday
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)

def parse_template(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def build_date_map(start_date: datetime, rows):
    date_map = []
    for r in rows:
        week = int(r["Week"])
        day = int(r["Day"]) if r["Day"].strip() else 1
        date = start_date + timedelta(days=(week - 1) * 7 + (day - 1))
        date_map.append(date)
    return date_map

def normalize_type(t: str) -> str:
    return t.strip()

def instructor_list(pref: str):
    pref = pref.strip().strip('"')
    if not pref:
        return []
    return [p.strip() for p in pref.split(',') if p.strip()]

def fetch_candidate(conn, template_type, duration_min, intensity_min, intensity_max, instructors, allow_fallback):
    """Attempt to find a matching class according to layered fallback strategy."""
    cur = conn.cursor()
    base_keywords = KEYWORD_MAP.get(template_type, [])
    # Special case: plain Power Zone should exclude Endurance/Max variants
    excludes = EXCLUDE_SUBSTRINGS_FOR_PURE_POWER_ZONE if template_type == "Power Zone" else []

    def run_query(duration_window, rating_window, restrict_instructors, allow_loose_title=False):
        params = []
        where = ["difficulty_rating IS NOT NULL"]
        # Duration filter
        if duration_window:
            low, high = duration_window
            where.append("duration_minutes BETWEEN ? AND ?")
            params.extend([low, high])
        # Rating filter
        if rating_window:
            rlow, rhigh = rating_window
            where.append("difficulty_rating BETWEEN ? AND ?")
            params.extend([rlow, rhigh])
        # Instructor preference
        if restrict_instructors and instructors:
            placeholders = ",".join(["?" for _ in instructors])
            where.append(f"instructor IN ({placeholders})")
            params.extend(instructors)
        # Title matching
        title_conditions = []
        if base_keywords and not allow_loose_title:
            for kw in base_keywords:
                title_conditions.append("title LIKE ?")
                params.append(f"%{kw}%")
        if template_type == "Power Zone" and not allow_loose_title:
            # Exclude Endurance/Max variants
            for ex in excludes:
                title_conditions.append("title NOT LIKE ?")
                params.append(f"%{ex}%")
        if template_type == "FTP Test" and not allow_loose_title:
            # Ensure 'Test' appears
            title_conditions.append("title LIKE ?")
            params.append("%Test%")
        if title_conditions:
            where.append("(" + " AND ".join(title_conditions) + ")")
        sql = (
            "SELECT id,title,instructor,duration_minutes,difficulty_rating,url,original_air_time "
            "FROM classes WHERE " + " AND ".join(where) + " ORDER BY RANDOM() LIMIT 1"
        )
        cur.execute(sql, params)
        return cur.fetchone()

    # Strategy layers
    rating_window = (intensity_min, intensity_max) if intensity_max > 0 else None
    duration_window = (duration_min, duration_min) if duration_min > 0 else None
    # 1. Strict all filters with instructor preference
    candidate = run_query(duration_window, rating_window, True)
    if candidate:
        return candidate
    # 2. Remove instructor restriction
    candidate = run_query(duration_window, rating_window, False)
    if candidate:
        return candidate
    # 3. Widen duration ±10, keep rating
    if duration_min > 0:
        candidate = run_query((max(1, duration_min - 10), duration_min + 10), rating_window, False)
        if candidate:
            return candidate
    # 4. Widen rating window gradually
    if allow_fallback and rating_window:
        widen_steps = [2.0, 3.0]
        for widen in widen_steps:
            rlow = max(0, rating_window[0] - widen)
            rhigh = min(10, rating_window[1] + widen)
            candidate = run_query(duration_window, (rlow, rhigh), False)
            if candidate:
                return candidate
    # 5. Drop rating filter entirely
    candidate = run_query(duration_window, None, False)
    if candidate:
        return candidate
    # 6. Loose title (just keyword presence relaxed) & wider duration
    candidate = run_query((max(1, duration_min - 15), duration_min + 15), None, False, allow_loose_title=True)
    return candidate

def generate_plan(args):
    template_rows = parse_template(args.template)
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else next_monday()
    date_map = build_date_map(start_date, template_rows)

    db_path = args.db_path
    if not os.path.exists(db_path):
        raise SystemExit(f"Database not found at {db_path}. Run refresh_cache.py first.")
    conn = sqlite3.connect(db_path)

    used_ids = set()
    output_rows = []
    unmatched = 0

    for row, ride_date in zip(template_rows, date_map):
        tpl_type = normalize_type(row["Type"])
        duration = int(row["Duration_Min"]) if row["Duration_Min"].strip() else 0
        imin = float(row["Intensity_Min"]) if row["Intensity_Min"].strip() else 0.0
        imax = float(row["Intensity_Max"]) if row["Intensity_Max"].strip() else 0.0
        instructors = instructor_list(row["Instructor_Preference"]) if "Instructor_Preference" in row else []
        notes = row.get("Notes", "")

        if tpl_type.lower() == "rest" or duration == 0:
            output_rows.append([
                row["Week"], ride_date.strftime("%Y-%m-%d"), row["Phase"], row["Day"], tpl_type,
                "", "", "", "", f"{imin}", f"{imax}", "", "", notes
            ])
            continue

        candidate = fetch_candidate(conn, tpl_type, duration, imin, imax, instructors, args.allow_fallback)
        # Avoid duplicates by retrying a few times
        retry = 0
        while candidate and candidate[0] in used_ids and retry < 5:
            candidate = fetch_candidate(conn, tpl_type, duration, imin, imax, instructors, args.allow_fallback)
            retry += 1

        if not candidate or candidate[0] in used_ids:
            unmatched += 1
            output_rows.append([
                row["Week"], ride_date.strftime("%Y-%m-%d"), row["Phase"], row["Day"], tpl_type,
                "", "NO MATCH", "", str(duration), f"{imin}", f"{imax}", "", "", notes
            ])
            continue

        class_id, title, instructor, dur, rating, url, air_time = candidate
        used_ids.add(class_id)
        output_rows.append([
            row["Week"], ride_date.strftime("%Y-%m-%d"), row["Phase"], row["Day"], tpl_type,
            class_id, title, instructor, str(dur), f"{imin}", f"{imax}", f"{rating}", url, notes
        ])

    conn.close()

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    out_path = out_dir / f"training-plan-{ts}.csv"
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Week","Date","Phase","Day","Template_Type","Selected_Class_ID","Title","Instructor","Duration","Intensity_Min","Intensity_Max","Difficulty_Rating","URL","Notes"
        ])
        writer.writerows(output_rows)

    print(f"\n[PLAN] Generated plan saved to {out_path}")
    print(f"[PLAN] Total rows: {len(output_rows)} | Unmatched: {unmatched}")
    if unmatched:
        print("[PLAN] Consider enabling --allow-fallback or broadening intensity ranges in template.")

def main():
    parser = argparse.ArgumentParser(description="Generate a training plan from a template CSV (uses ALL classes)")
    parser.add_argument("--template", default="input/8-week-plan.csv", help="Template CSV path")
    parser.add_argument("--start-date", help="Start date for Week 1 Day 1 (YYYY-MM-DD); default next Monday")
    parser.add_argument("--db-path", default=DEFAULT_DB, help="SQLite DB path")
    parser.add_argument("--allow-fallback", action="store_true", help="Enable broader fallback matching when strict match fails")
    args = parser.parse_args()
    generate_plan(args)

if __name__ == "__main__":
    main()
