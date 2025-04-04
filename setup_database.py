import sqlite3

# ✅ Connect to SQLite database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ✅ Create table for storing arguments
cursor.execute("""
    CREATE TABLE IF NOT EXISTS arguments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        topic TEXT,
        argument TEXT,
        score REAL,
        feedback TEXT
    )
""")

# ✅ Create table for timer usage (this was missing!)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS usage (
        email TEXT PRIMARY KEY,
        practice_time INTEGER DEFAULT 0,
        real_debate_time INTEGER DEFAULT 0
    )
""")

# ✅ Save and close
conn.commit()
conn.close()

print("✅ Database and tables created successfully!")
