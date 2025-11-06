import sqlite3
import os

base_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith('sqlite'):
    # Expect format sqlite:///./file.db or sqlite:///absolute/path
    db_path_part = db_url.split('sqlite:///')[-1]
    if db_path_part.startswith('./'):
        db_path = os.path.normpath(os.path.join(base_dir, db_path_part[2:]))
    else:
        db_path = os.path.normpath(db_path_part)
else:
    db_path = os.path.join(base_dir, 'dev.db')

print('DB path:', db_path)
print('DB exists:', os.path.exists(db_path))

con = sqlite3.connect(db_path)
cur = con.cursor()

for name in ('users', 'tickets', 'messages'):
    row = cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
    print(f"\nDDL for {name}:")
    print(row[0] if row else 'NOT FOUND')

con.close()