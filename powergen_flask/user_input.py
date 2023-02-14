"""

    GUI Implementation - User Inputs

    "Energy For Development" VIP (University of Strathclyde)

    Code by Andrew Ward and Ella Sherwood

"""

import functools, os
import pandas as pd
import customer_clustering as cc
import network_designer as nd

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from powergen_flask.db import get_db

# create a blueprint for implementing the customer clustering based on user inputs
bp = Blueprint('user_input', __name__)


@bp.route('/user_input', methods=('GET', 'POST'))
# this function takes inputs based on the parameters of the CustomerClustering.py class
def user_input():
    if request.method == 'POST':
        network_voltage = float(request.form['Network Voltage'])
        pole_cost = float(request.form['Pole Cost'])
        pole_spacing = float(request.form['Pole Spacing'])
        resistance_per_km = float(request.form['Resistance per km'])
        current_rating = float(request.form['Current Rating'])
        cost_per_km = float(request.form['Cost per km'])
        max_voltage_drop = float(request.form['Max Voltage Drop'])

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

                return render_template('input/results.html')
    return render_template('input/input.html')

# Parsing the CSV File CG
# def parseCSV(filePath):
#     # CVS Column Names
#     col_names = ['network voltage','pole cost' , 'pole spacing', 'resistance per_km' ,'current rating' , 'cost per km','max voltage_drop' ]
#     # Use Pandas to parse the CSV file
#     csvData = pd.read_csv(filePath, names=col_names, header=None)
#     # Loop through the Rows
#     for i, row in csvData.iterrows():
#         print(i, row ['network_voltage'], row['pole_cost'], row['pole_spacing'], row['resistance_per_km'],row['current_rating'],row[' cost_per_km'],row['max_voltage_drop'])
#
# import mysql.connector
#
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="root",
#   password="",
#   database="PowerGen"#
# )
#
# def parseCSV(file_path):
#     # CSV Column Names
#     col_names
