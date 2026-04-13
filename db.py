import sqlite3

conn = sqlite3.connect("notes.db")
cursor = conn.cursor()

# USERS TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
""")

# NOTES TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
title TEXT,
category TEXT,
filename TEXT,
status TEXT
)
""")

conn.commit()
conn.close()

print("DATABASE READY")