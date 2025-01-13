from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import requests

app = Flask(__name__)
app.secret_key = 'secret_key'  # Ganti dengan kunci rahasia yang lebih aman

# Path database utama untuk user dan admin
DB_PATH = 'APPX/app_db.sqlite'

# Membuat database untuk login jika belum ada
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL  -- "admin" atau "user"
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            input_data TEXT NOT NULL,
            location TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

# Halaman utama
@app.route('/')
def index():
    return render_template('index.html')

# Halaman register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'user'  # Default role adalah user
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?);", 
                           (username, password, role))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists. Please choose another."
    return render_template('register.html')

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?;", 
                       (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]
            if user[3] == 'admin':  # Jika admin
                return redirect(url_for('dashboard'))
            else:  # Jika user
                return redirect(url_for('user_input'))
        return "Invalid username or password."
    return render_template('login.html')

# Halaman admin dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Filter input berdasarkan lokasi
        if request.method == 'POST':
            location = request.form['location']
            if location:  # Jika lokasi dipilih
                cursor.execute('SELECT id, username, input_data, location, timestamp FROM inputs WHERE location = ?', (location,))
            else:  # Jika "All Locations" dipilih (location kosong)
                cursor.execute('SELECT id, username, input_data, location, timestamp FROM inputs')
        else:
            # Default: Tampilkan semua data
            cursor.execute('SELECT id, username, input_data, location, timestamp FROM inputs')

        inputs = cursor.fetchall()

        # Ambil semua user
        cursor.execute('SELECT id, username, password, role FROM users')
        users = cursor.fetchall()

        # Ambil daftar lokasi unik untuk dropdown
        cursor.execute('SELECT DISTINCT location FROM inputs')
        locations = cursor.fetchall()

        conn.close()

        return render_template('dashboard.html', inputs=inputs, users=users, locations=locations)
    else:
        flash("Unauthorized access. Please log in as admin.")
        return redirect('/login')


# Halaman user input
@app.route('/user-input', methods=['GET', 'POST'])
def user_input():
    if 'role' in session and session['role'] == 'user':
        if request.method == 'POST':
            username = session['username']
            input_data = request.form['input_data']
            location = request.form['location']

            # Simpan data ke database
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO inputs (username, input_data, location) VALUES (?, ?, ?)',
                (username, input_data, location)
            )
            conn.commit()
            conn.close()

            flash('Data berhasil disimpan!')
            return redirect('/user-input')

        return render_template('user_input.html')
    else:
        flash("Unauthorized access. Please log in as a user.")
        return redirect('/login')
    
    # Rute untuk menghapus user
@app.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        flash("User berhasil dihapus!")
        return redirect(url_for('dashboard'))
    else:
        flash("Unauthorized access.")
        return redirect('/login')

# Rute untuk menghapus input data
@app.route('/delete-input/<int:input_id>', methods=['POST'])
def delete_input(input_id):
    if 'role' in session and session['role'] == 'admin':
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inputs WHERE id = ?', (input_id,))
        conn.commit()
        conn.close()
        flash("Input data berhasil dihapus!")
        return redirect(url_for('dashboard'))
    else:
        flash("Unauthorized access.")
        return redirect('/login')


# Fungsi untuk mengecek status microservices
def check_service_status(url):
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return "Online"
    except requests.exceptions.RequestException:
        return "Offline"
    return "Unknown"

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()  # Inisialisasi database saat pertama kali
    app.run(port=5000, debug=True)
