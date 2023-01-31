"""

    GUI Implementation - User Inputs

    "Energy For Development" VIP (University of Strathclyde)

    Code by Andrew Ward and Ella Sherwood

"""

import functools, os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from powergen_flask.db import get_db

# create a blueprint for implementing the customer clustering based on user inputs
bp = Blueprint('input', __name__, url_prefix='/input')


@bp.route('/cluster', methods=('GET', 'POST'))
# this function takes inputs based on the parameters of the CustomerClustering.py class
def cluster():
    if request.method == 'POST':
        network_voltage = request.form['Network Voltage']
        pole_cost = request.form['Pole Cost']
        pole_spacing = request.form['Pole Spacing']
        resistance_per_km = request.form['Resistance per km']
        current_rating = request.form['Current Rating']
        cost_per_km = request.form['Cost per km']
        max_voltage_drop = request.form['Max Voltage Drop']

        error = None
        db = get_db()

        # upload CSV file into static folder
        csv_file = request.files['CSV File']
        if csv_file.filename != '':
            # set the file path
            file_path = os.path.join('powergen_flask/static/files', csv_file.filename)
            # save the file
            csv_file.save(file_path)

        # inserts relevant info into database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO inputs (network_voltage, pole_cost, pole_spacing, resistance_per_km, current_rating, cost_per_km, max_voltage_drop) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (network_voltage, pole_cost, pole_spacing, resistance_per_km, current_rating, cost_per_km,
                     max_voltage_drop),
                )
                db.commit()
            except db.IntegrityError:
                error = "Integrity Error!"
            else:
                return render_template('input/cluster_results.html')

        # add a way of inserting these values from the SQLite database into the Clustering Subsystem
    return render_template('input/cluster.html')
