import sqlite3

# Membuat Database A (db_a.sqlite)
def create_db_a():
    conn = sqlite3.connect('SiteA/db_a.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
    print("Database A created successfully!")

# Membuat Database B (db_b.sqlite)
def create_db_b():
    conn = sqlite3.connect('SiteB/db_b.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            info TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
    print("Database B created successfully!")

if __name__ == '__main__':
    create_db_a()
    create_db_b()
