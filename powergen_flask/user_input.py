"""

    GUI Implementation - User Inputs

    "Energy For Development" VIP (University of Strathclyde)

    Code by Andrew Ward and Ella Sherwood

"""

import functools, os
import pandas as pd
import customer_clustering as cc
import network_designer as nd
import gensizer as gs
import random
import pvoutput as pv

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from powergen_flask.db import get_db

# create a blueprint for implementing the customer clustering based on user inputs
bp = Blueprint('user_input', __name__)

# This should be user defined - in latitude/longitude or by clicking
source_location = (135, -150)

# coordinates for Jiboro in The Gambia - should also be user defined - all they are used for at the moment is the
# Renewables.Ninja API query
latitude = 13.17
longitude = -16.57

# will create a generation sizer object with 50 particles
num_particles = 50

# what is this? have decided to leave it out of the form for now
timebreakerMax = 0


@bp.route('/user_input', methods=('GET', 'POST'))
# this function takes inputs based on the parameters of the CustomerClustering.py class
def user_input():
    if request.method == 'POST':
        # Parameters for Customer Clustering
        network_voltage = float(request.form['Network Voltage'])
        pole_cost = float(request.form['Pole Cost'])
        pole_spacing = float(request.form['Pole Spacing'])
        resistance_per_km = float(request.form['Resistance per km'])
        current_rating = float(request.form['Current Rating'])
        cost_per_km = float(request.form['Cost per km'])
        max_voltage_drop = float(request.form['Max Voltage Drop'])

        # Parameters for Generation Sizer
        num_particles = int(request.form['Number of Particles'])
        pv_capacity = float(request.form['PV Panel Capacity'])
        solCost = float(request.form['PV Panel Cost'])
        battCost = float(request.form['Battery Cost'])
        genCost = float(request.form['Diesel Generator Cost'])
        fuelCost = float(request.form['Fuel Cost'])
        EbattMax_unit = float(request.form['Max Battery Energy'])
        EbattMin_unit = float(request.form['Min Battery Energy'])
        Pgen_unit = float(request.form['Diesel Generator Rated Power'])
        fuelReq = float(request.form['Fuel Requirement'])
        timebreakerMax = int(request.form['Required Days of Autonomy'])
        autonomDaysMin = int(request.form['Required Days of Autonomy'])

        error = None
        db = get_db()

        # upload CSV file into static folder
        csv_file = request.files['CSV File']
        if csv_file.filename != '':
            # set the file path
            file_path = os.path.join('powergen_flask/static/files', csv_file.filename)
            # save the file
            csv_file.save(file_path)

            # it would be best practice to insert the coordinates into the database for easier retrieval etc.

        # inserts relevant info into database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO inputs (network_voltage, pole_cost, pole_spacing, resistance_per_km, current_rating, cost_per_km, max_voltage_drop, file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (network_voltage, pole_cost, pole_spacing, resistance_per_km, current_rating, cost_per_km,
                     max_voltage_drop, file_path),
                )
                db.commit()
            except db.IntegrityError:
                error = "Integrity Error!"
            else:
                # this is where the code goes once it has inserted everything into the database

                # the import_from_csv() function developed by A.S. but with inputs from the form
                clusterer = cc.CustomerClustering.import_from_csv(
                    file_path,
                    network_voltage=network_voltage,
                    pole_cost=pole_cost,
                    pole_spacing=pole_spacing,
                    resistance_per_km=resistance_per_km,
                    current_rating=current_rating,
                    cost_per_km=cost_per_km,
                    max_voltage_drop=max_voltage_drop
                )
                # The following code is adapted from AS's demo_all_subsystems.py file
                # STEP 1: CLUSTER THE CUSTOMERS TOGETHER
                clusterer.cluster()

                # retrieve clusters - these are the nodes used in the network designer
                nodes = clusterer.clusters

                # STEP 2 - RETICULATION DESIGN
                # get locations and power demands of each node (cluster objects)
                nodes_locs = [node.position for node in nodes]
                nodes_Pdem = [node.Pdem_total for node in nodes]
                # nodes power demands is a list of arrays - each array is yearly demand for single node

                # create designer object with defined network parameters and nodes
                designer = nd.NetworkDesigner(
                    source_location,
                    nodes_locs,
                    nodes_Pdem,
                    network_voltage,
                    pole_cost,
                    pole_spacing,
                    resistance_per_km,
                    current_rating,
                    cost_per_km
                )

                # build the actual network
                designer.build_network()

                # STEP 3 - RETRIEVING ESTIMATED PV OUTPUT

                # rng seed
                random.seed(420)

                # total power demand is sum of all cluster (node) demands
                total_Pdem = 0
                for pdem in nodes_Pdem:
                    total_Pdem += pdem
                # make yearly profile from daily profile
                total_Pdem = list(total_Pdem) * 365

                # retrieve estimated single PV panel output
                output_pv_unit = pv.pv_output(
                    latitude,
                    longitude,
                    pv_capacity,
                    year=2019,
                    auto_dataset=True,
                    auto_tilt=True
                )

                # STEP 4 - OPTIMISE GENERATION MIX WITH GENSIZER

                sizer = gs.GenSizer(
                    num_particles,
                    total_Pdem,
                    output_pv_unit,
                    solCost,
                    battCost,
                    genCost,
                    fuelCost,
                    EbattMax_unit,
                    EbattMin_unit,
                    Pgen_unit,
                    fuelReq,
                    timebreakerMax,
                    autonomDaysMin
                )
                # this redirect takes the user to the next page, for which the redirect is defined below
                return redirect(url_for('user_input.results'))
    return render_template('input/input.html')


@bp.route('/user_input/results', methods=('GET','POST'))
def results():
    return render_template('input/results.html')
