# -*- coding: utf-8 -*-
"""
    This example demonstrates how to use the NetworkDesigner object
    with data from a CSV file. 
"""

import time

import numpy as np
import matplotlib.pyplot as plt
import network_designer as nd
import networkx as nx

t1 = time.time()

network_voltage = 230  # V
pole_cost = 100  # £
pole_spacing = 50  # m
res_per_km = 4.61  # ohm/km
max_current = 37  # A
cost_per_km = 1520  # £/km
max_volt_drop = 11.5  # V

net = nd.NetworkDesigner.import_from_csv(
    "nodes.csv",
    network_voltage,
    pole_cost,
    pole_spacing,
    res_per_km,
    max_current,
    cost_per_km,
    max_V_drop=max_volt_drop
)

# net = nd.NetworkDesigner.import_from_csv("nodes.csv", network_voltage, res_per_km, max_current, cost_per_km,
#     scl=1, max_V_drop=11.5) 

net.build_network()
net.draw_graph(save=True)
print("total network Pdem:",net.total_Pdem, "W")
print("\nnetwork cost: £", round(net.total_cost,2))
print("\ntotal length:", round(net.total_length,2), "m")

t2 = time.time()
print("\n-------------------------------")
print("elapsed time: " + str(t2-t1))
