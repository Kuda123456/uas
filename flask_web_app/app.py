import logging
import uuid
from flask import Flask, render_template, request, redirect, url_for
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime

app = Flask(__name__)

# Konfigurasi kunci rahasia untuk enkripsi token
app.config['SECRET_KEY'] = 'mysecretkey'

# Data sementara untuk menyimpan pengguna
users = []

# Menyimpan log aktivitas dalam list (atau bisa juga ke file)
log_data = []

# Fungsi untuk menghasilkan token aman
def generate_token(user_id):
    s = Serializer(app.config['SECRET_KEY'])
    return s.dumps({'user_id': user_id})  # Hapus bagian .decode('utf-8')

# Fungsi untuk memverifikasi token
def verify_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=3600)  # Token berlaku selama 1 jam
    except:
        return None
    return data['user_id']

# Fungsi untuk mencatat log dengan format yang diinginkan
def log_user_activity(user_id, action, role, ip_addr):
    log_id = str(uuid.uuid4())  # Membuat UUID unik
    status = "HTTPAccess" if role != "GUEST" else "INTRUDER"  # Menentukan status (GUEST atau user)
    app_name = "PBL01LOGS"
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    log_entry = {
        'UUID': log_id,
        'KEY': status,
        'TXT': action,
        'SESSION': f'user{user_id}' if user_id else "GUEST",
        'IPADDR': ip_addr,
        'APP': app_name,
        'TIME': timestamp
    }
    log_data.append(log_entry)  # Menambahkan log ke daftar log_data

# Halaman utama (Landing page)
@app.route('/')
def index():
    return render_template('index.html')

# Halaman registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']  # Menambahkan pilihan role (user atau admin)
        user_id = len(users) + 1
        users.append({'user_id': user_id, 'username': username, 'password': password, 'role': role})
        # Buat token untuk pengguna setelah registrasi
        token = generate_token(user_id)
        log_user_activity(user_id, 'Sign Up', role, request.remote_addr)  # Mencatat log saat signup
        return redirect(url_for('welcome', token=token))
    return render_template('register.html')

# Halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Cek kredensial pengguna
        for user in users:
            if user['username'] == username and user['password'] == password:
                # Buat token untuk pengguna yang berhasil login
                token = generate_token(user['user_id'])
                log_user_activity(user['user_id'], 'Sign In', user['role'], request.remote_addr)  # Mencatat log saat login
                if user['role'] == 'admin':  # Jika admin, arahkan ke halaman admin
                    return redirect(url_for('admin_dashboard', token=token))
                else:  # Jika user biasa, arahkan ke halaman welcome
                    return redirect(url_for('welcome', token=token))
        return 'Invalid credentials, please try again.'
    return render_template('login.html')

# Halaman sambutan setelah login atau registrasi
@app.route('/welcome')
def welcome():
    token = request.args.get('token')
    user_id = verify_token(token)
    if user_id:
        # Cari pengguna berdasarkan user_id
        user = next(user for user in users if user['user_id'] == user_id)
        return f'Welcome, {user["role"]} User {user_id}!'
    else:
        return 'Invalid or expired token.'

# Halaman dashboard admin
@app.route('/admin_dashboard')
def admin_dashboard():
    token = request.args.get('token')
    user_id = verify_token(token)
    if user_id:
        # Cari pengguna berdasarkan user_id
        admin_user = next(user for user in users if user['user_id'] == user_id)
        if admin_user['role'] == 'admin':  # Verifikasi apakah yang login adalah admin
            # Menampilkan log aktivitas di dashboard admin
            return render_template('admin_dashboard.html', log_data=log_data)
        else:
            return 'Access denied. You are not an admin.'
    else:
        return 'Invalid or expired token.'

if __name__ == '__main__':
    app.run(debug=True)
