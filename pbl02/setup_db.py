import sqlite3

# Membuat koneksi ke database
conn = sqlite3.connect('cars.db')
c = conn.cursor()

# Membuat tabel cars
c.execute('''CREATE TABLE IF NOT EXISTS cars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    make TEXT NOT NULL,
    model TEXT NOT NULL,
    year INTEGER NOT NULL,
    price REAL NOT NULL
)''')

# Menyimpan perubahan dan menutup koneksi
conn.commit()
conn.close()

print("Database and tables created successfully!")
