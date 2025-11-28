import sqlite3

def main():
    conn = sqlite3.connect("peloton_classes.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id TEXT PRIMARY KEY,
        title TEXT,
        instructor TEXT,
        duration_minutes INTEGER,
        difficulty_rating REAL,
        class_type TEXT,
        original_air_time TEXT,
        url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    c.execute("""
    CREATE INDEX IF NOT EXISTS idx_type_duration_difficulty
    ON classes(class_type, duration_minutes, difficulty_rating);
    """)
    conn.commit()
    conn.close()
    print("Database ready")

if __name__ == "__main__":
    main()
