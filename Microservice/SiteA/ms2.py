from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DB_PATH = 'db_a.sqlite'

# Endpoint untuk operasi khusus di MS2
@app.route('/ms2', methods=['GET'])
def get_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data;")
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/ms2', methods=['POST'])
def add_data():
    try:
        data = request.json
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO data (info) VALUES (?);", (data['info'],))
        conn.commit()
        conn.close()
        return jsonify({"message": "Data added to DB-A via MS2"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5052, debug=True)
