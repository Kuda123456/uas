from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import sqlite3
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder untuk menyimpan file CSV

# Fungsi untuk membuat tabel cars
def create_table():
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT,
        model TEXT,
        year INTEGER,
        price REAL
    )''')
    conn.commit()
    conn.close()

create_table()

# Rute untuk menampilkan semua mobil di database
@app.route('/')
def index():
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    c.execute("SELECT * FROM cars")
    cars = c.fetchall()
    conn.close()
    return render_template('index.html', cars=cars)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            
            # Membaca file CSV dan memasukkan data ke dalam database
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                conn = sqlite3.connect('cars.db')
                c = conn.cursor()
                for row in reader:
                    if len(row) == 4:  # Memastikan ada 4 kolom pada baris CSV
                        c.execute("INSERT INTO cars (make, model, year, price) VALUES (?, ?, ?, ?)", 
                                  (row[0], row[1], row[2], row[3]))  # Menggunakan row[0] hingga row[3]
                    else:
                        print(f"Skipping invalid row: {row}")  # Baris tidak valid
                conn.commit()
                conn.close()
            flash('CSV file uploaded and data inserted successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid file format. Please upload a CSV file.', 'error')
    return render_template('upload.html')


# Rute untuk mengedit data mobil
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        price = request.form['price']
        
        c.execute("UPDATE cars SET make=?, model=?, year=?, price=? WHERE id=?", 
                  (make, model, year, price, id))
        conn.commit()
        conn.close()
        flash('Car data updated successfully!', 'success')
        return redirect(url_for('index'))

    c.execute("SELECT * FROM cars WHERE id=?", (id,))
    car = c.fetchone()
    conn.close()
    return render_template('edit.html', car=car)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_term = request.form['search']
        conn = sqlite3.connect('cars.db')
        c = conn.cursor()
        c.execute("SELECT * FROM cars WHERE make LIKE ? OR model LIKE ? OR year LIKE ?",
                  ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
        cars = c.fetchall()
        conn.close()
        return render_template('index.html', cars=cars)
    return redirect(url_for('index'))

# Rute untuk menghapus data mobil
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect('cars.db')
    c = conn.cursor()
    c.execute("DELETE FROM cars WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash('Car data deleted successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
