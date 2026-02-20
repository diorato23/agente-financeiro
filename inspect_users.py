import sqlite3
import os

db_path = "data/financeiro.db"
if not os.path.exists(db_path):
    print("Database not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Columns for 'users':")
    for col in columns:
        print(f" - {col[1]} ({col[2]})")
    conn.close()
