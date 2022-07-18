# -*- coding: utf-8 -*-
"""

    Customer Clustering for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)

"""

import numpy as np
import pandas as pd
import k_means_constrained as kms

def import_nodes_from_csv(scale_factor=1):
    
    scale = scale_factor
    
    # read CSV file
    df = pd.read_csv("nodes.csv")
    df = df.set_index("ID")
    
    nodes = []
    
    # create source and node objects from entries in CSV
    source = True
    for node_id,data in df.iteritems():
        # first entry is source
        if source:
            source_location = [scale * int(data[0]), scale * int(data[1])]
            nodes.append(Source(source_location))
            source = False
        # rest are nodes
        else:
            location = [scale * int(data[0]), scale * int(data[1])]
            power_demand = data[2:].tolist()
            nodes.append(Node(location, node_id, power_demand))