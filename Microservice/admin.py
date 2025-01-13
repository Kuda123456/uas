import sqlite3

conn = sqlite3.connect('APPX/app_db.sqlite')
cursor = conn.cursor()

# Buat tabel inputs jika belum ada
cursor.execute('''
CREATE TABLE IF NOT EXISTS inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    input_data TEXT,
    location TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
print("Tabel inputs berhasil dibuat!")
