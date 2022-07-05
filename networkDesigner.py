# -*- coding: utf-8 -*-
"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""
"""
FUTURE WORK

- create (potentially external) function to extract info (location etc) from KML files directly

"""
import pandas as pd
import numpy as np
from math import sqrt


class Node:
    
    def __init__(self, location, power_demand, customer_id):
        
        # customer ID displayed in final plot
        self.customer_id = str(customer_id)
        
        # location is tuple with X-Y coordinates
        self.loc = tuple(location)
        
        # power demand is list-like object
        self.pdem = power_demand
        
        # voltage & current arrays
        self.volt = [0]*len(power_demand)
        self.curr = [0]*len(power_demand)
        
        # line resistance (between itself and parent node)
        self.res_line = 0
        
        # line current (between itself and parent node)
        self.curr_line = [0]*len(power_demand)

        # status indicators for constraints check
        self.current_calculated = False
        self.voltage_calculated = False
        
        # constraint checker (initially true)
        self.constraint_satisfied = True
        
        # index of gate node top of subtree
        # initially itself, set with __init_subtree method
        self.subtree = None
        
        # index of parent node
        # initially source node (index 0)
        self.parent = 0
        
        self.cost = 0
    
    def isgate(self):
        
        if self.parent == 0:
            return True


class Source:
    
    def __init__(self, location):
        
        self.customer_id = "SOURCE"
        
        self.loc = tuple(location)


class NetworkDesigner:
    
    def __init__(self, network_voltage):
        
        self.Vnet = network_voltage
    
    def import_customers(self, scale=1):
        
        # !!! REPLACED WITH KML READER LATER
        
        df = pd.read_csv("customers.csv")
        df = df.set_index("ID")
        
        self.nodes = []
        
        # !!! TRY REPLACING WITH MAP FUNCTION
        source = True
        for customer_id,data in df.iteritems():
            # first entry is source
            if source:
                source_location = [scale * int(data[0]), scale * int(data[1])]
                self.nodes.append(Source(source_location))
                source = False
            else:
                location = [scale * int(data[0]), scale * int(data[1])]
                power_demand = data[2:].tolist()
                self.nodes.append(Node(location, power_demand, customer_id))
    
    def __init_subtrees(self):
        """
        For initialisation phase only. Sets subtree of each node as node itself.
        
        """

        for index, node in enumerate(self.nodes):
            # source node excluded
            if str(type(node)) == "Source":
                pass
            else:
                node.subtree = index
    
    def __init_matrices(self):
        """
        For initialisation phase only. Creates adjacency, distance and checked path matrices for CMST.
        
        """

        size = (len(self.nodes), len(self.nodes))
        
        # initially no nodes connected to each other
        self.adj_matrix = np.zeros(size)
        # create distance matrix
        self.dist_matrix = np.zeros(size)
        # create path check matrix (paths between node and itself set as checked (True))
        self.path_check_matrix = np.eye(size[0], dtype=bool)
        
        # populate distance matrix with distances
        # and connect all nodes to source
        for index1,node1 in enumerate(self.nodes):
            for index2,node2 in enumerate(self.nodes):
                x1 = node1.loc[0]
                y1 = node1.loc[1]
                
                x2 = node2.loc[0]
                y2 = node2.loc[1]
                
                distance = sqrt((y2-y1)**2 + (x2-x1)**2)
                
                self.dist_matrix[index1,index2] = distance
                
                # if calulcating the distance between source and node
                # connect them in adj matrix
                if type(node1) == Source or type(node2) == Source:
                    self.adj_matrix[index1,index2] = distance
                    
                    
    def cable_specs(self, resistance_per_km, current_rating, cost_per_km):
        # !!! future: add similar import to customers for cables
        
        # convert units to ohm per meter
        self.res_per_meter = resistance_per_km / 1000
        self.Imax = current_rating
        # convert untis to dollars per meter
        self.cost_per_meter = cost_per_km / 1000
    
    def build_network(self):

        # INITIALISATION PHASE
        
        # !!! might want to make it external (program calls before .build_network())
        self.import_customers(scale=1)     # !!! scale factor goes here
        
        # set initial subtrees
        self.__init_subtrees()
        # create adjacency / distance / path check matrices
        self.__init_matrices()

"""
TESTING AREA
"""

n = NetworkDesigner(240)
n.import_customers()
n._NetworkDesigner__init_subtrees()
n._NetworkDesigner__init_matrices()