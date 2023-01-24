"""

    GUI Implementation - User Inputs

    "Energy For Development" VIP (University of Strathclyde)

    Code by Andrew Ward and Ella Sherwood

"""

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

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
        max_voltage_drop = request.form['Maximum voltage drop']

    return render_template('input/cluster.html')