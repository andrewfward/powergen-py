# -*- coding: utf-8 -*-
"""
    Illustrates how all subsystems interact with eachother.
"""


import random

import numpy as np

import customer_clustering as cc
import network_designer as nd
import PVOutput as pv
import genSizer as gs


# STEP 0 - DEFINING PARAMETERS

# NETWORK PARAMETERS
max_connections = 6 # maximum possible connections per pole
network_voltage = 230 # V
pole_cost = 100 # $ (or any other currency)
pole_spacing = 50 # m
resistance_per_km = 4.61 # ohm/km
current_rating = 37 # A
cost_per_km = 1520 # $/km (or any other currency)
max_voltage_drop = 11.5 # V

source_location = (135,-150)

# GENERATION SIZER PARAMETERS
solCost = 150.98
battCost = 301.71
genCost = 320
fuelCost = 0.32

pv_capacity = 250
EbattMax_unit = 2040
EbattMin_unit = 408
Pgen_unit = 750
fuelReq = 1
timebreakerMax = 0
autonomDaysMin = 2


# STEP 1 - CLUSTER CUSTOMERS TOGETHER

# creat cluster object from CSV with parameters
file = "nodes_datapdem.csv"
clusterer = cc.CustomerClustering.import_from_csv(
    file,
    max_connections,
    network_voltage,
    pole_cost,
    pole_spacing,
    resistance_per_km,
    current_rating,
    cost_per_km,
    max_voltage_drop=11.5
    )

# cluster the customers together
clusterer.cluster()

# retrieve clusters - these are the nodes used in the network designer
nodes = clusterer.clusters


# STEP 2 - RETICULATION DESIGN

# get locations and power demands of each node (cluster objects)
nodes_locs = [node.position for node in nodes]
nodes_Pdem = [node.Pdem_total for node in nodes]
# nodes power demands is a list of arrays - each array is yearly demand for single node

# create designer object with network parameters and nodes
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

# build network and draw graph
designer.build_network()
designer.draw_graph()


# STEP 3 - RETRIEVING ESTIMATED PV OUTPUT

# rng seed
random.seed(420)

# coordinates for Jiboro in The Gambia
latitude = 13.17
longitude = -16.57

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

# create generation sizer object with 50 particles
num_particles = 50
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

# optimise generation mix
# switch animate to True to see 3D preview of PSO in action
# note: slows down performance noticeably 
max_iterations = 300
sizer.optimise(max_iterations, animate=False, final_plot=False)