from flask import Flask, render_template, jsonify, request
import sqlite3
import math

app = Flask(__name__)

class Point:
    def __init__(self, lat, lng, label, origin=None):
        self.lat = lat
        self.lng = lng
        self.label = label
        self.origin = origin
        self.distance = 0

    def set_origin(self, origin):
        self.origin = origin
        self.calculate_distance()

    def calculate_distance(self):
        R = 6371  # Radius of the Earth in kilometers
        lat1, lng1 = math.radians(self.lat), math.radians(self.lng)
        lat2, lng2 = math.radians(self.origin.lat), math.radians(self.origin.lng)
        dlat, dlng = lat2 - lat1, lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        self.distance = R * c * 1000

points = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/store-point', methods=['POST'])
def store_point():
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])
    label = request.form['label']

    if len(points) == 0:
        # If no points have been saved yet, use the current point as the origin point
        point = Point(lat, lng, label)
        points.append(point)
    else:
        # Otherwise, create a new point and set the origin point and distance
        point = Point(lat, lng, label, points[0])
        point.set_origin(points[0])
        points.append(point)

    # Store the point in the SQLite database
    conn = sqlite3.connect('points.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS points (lat REAL, lng REAL, label TEXT, origin_lat REAL, origin_lng REAL, distance REAL)')
    if point.origin is None:
        c.execute('INSERT INTO points (lat, lng, label, origin_lat, origin_lng, distance) VALUES (?, ?, ?, ?, ?, ?)',
              (lat, lng, label, None, None, 0))
    else:
        c.execute('INSERT INTO points (lat, lng, label, origin_lat, origin_lng, distance) VALUES (?, ?, ?, ?, ?, ?)',
              (lat, lng, label, point.origin.lat, point.origin.lng, point.distance))
    conn.commit()
    conn.close()

    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
