import sqlite3
import os

db_path = "data/financeiro.db"
if not os.path.exists(db_path):
    print("Database not found")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Adding missing columns to 'users' table...")
    
    columns_to_add = [
        ("full_name", "VARCHAR"),
        ("phone", "VARCHAR"),
        ("birth_date", "DATE"),
        ("currency", "VARCHAR DEFAULT 'COP'"),
        ("is_subscriber", "BOOLEAN DEFAULT 0")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f" - Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f" - Column {col_name} already exists.")
            else:
                print(f" - Error adding {col_name}: {e}")
    
    conn.commit()
    conn.close()
    print("Migration finished.")
