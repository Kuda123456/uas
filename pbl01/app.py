from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Fungsi untuk menghubungkan ke database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Halaman Utama (Menampilkan Postingan)
@app.route('/')
def index():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY post_time DESC")
    posts = c.fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

# Halaman Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Simpan data ke database
        try:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                      (username, password, email))
            conn.commit()
            conn.close()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another one.', 'error')
    
    return render_template('register.html')

# Halaman Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", 
                  (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('profile', username=username))
        else:
            flash('Invalid username or password', 'error')
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM posts ORDER BY post_time DESC")
    posts = c.fetchall()
    conn.close()

    return render_template('login.html', posts=posts)

# Halaman Profile
@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    if 'username' not in session or session['username'] != username:
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        text = request.form['text']
        post_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO posts (username, text, post_time) VALUES (?, ?, ?)", 
                  (username, text, post_time))
        conn.commit()

    c.execute("SELECT * FROM posts WHERE username = ? ORDER BY post_time DESC", (username,))
    posts = c.fetchall()
    conn.close()

    return render_template('profile.html', username=username, posts=posts)

# Halaman Admin Dashboard
@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'username' not in session or session['username'] != 'admin':
        return redirect(url_for('login'))

    conn = get_db_connection()
    c = conn.cursor()

    if request.method == 'POST':
        # Admin dapat memposting teks
        text = request.form['text']
        post_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO posts (username, text, post_time) VALUES (?, ?, ?)", 
                  ('admin', text, post_time))
        conn.commit()

    # Ambil data pengguna dan postingan
    c.execute("SELECT * FROM users")
    users = c.fetchall()

    c.execute("SELECT * FROM posts ORDER BY post_time DESC")
    posts = c.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', users=users, posts=posts)

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    app.run(debug=True)
