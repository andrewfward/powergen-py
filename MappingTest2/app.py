from flask import Flask, render_template, jsonify, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/store-point', methods=['POST'])
def store_point():
    lat = request.form['lat']
    lng = request.form['lng']
    label = request.form['label']

    # Store the point in the SQLite database
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS points (lat REAL, lng REAL, label TEXT)')
    c.execute('INSERT INTO points VALUES (?, ?, ?)', (lat, lng, label))
    conn.commit()
    conn.close()

    return jsonify({'success': True})

