import sqlite3

conn = sqlite3.connect("hr_management.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS hr_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    location TEXT,
    job_type TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    applicant_name TEXT,
    email TEXT,
    phone TEXT,
    resume_path TEXT
)
""")

conn.commit()
conn.close()
print("Database created successfully")
