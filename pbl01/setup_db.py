import sqlite3

# Membuat koneksi ke database SQLite
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Membuat tabel users
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
)''')

# Membuat tabel posts
c.execute('''CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    text TEXT NOT NULL,
    post_time TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users (username)
)''')

# Menyimpan perubahan dan menutup koneksi
conn.commit()
conn.close()

print("Database and tables created successfully!")
