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
        self.res_line = None # !!!
        
        # line current (between itself and parent node)
        self.curr_line = [0]*len(power_demand)

        # status indicators for constraints check
        self.current_calculated = False
        self.voltage_calculated = False
        
        # constraint checker (initially true)
        self.constraint_satisfied = True
        
        # index of gate node top of subtree
        # initially source node (index 0)
        self.subtree = 0
        
        # index of parent node
        # initially source node (index 0)
        self.parent = 0
        
        self.cost = 0
    
    def isgate(self):
        
        if self.parent == 0:
            return True
        pass

class Source:
    
    def __init__(self, location):
        
        self.customer_id = "SOURCE"
        
        self.loc = tuple(location)

class NetworkDesigner:
    
    def __init__(self):
        pass
    
    def import_customers(self, scale=1):
        
        df = pd.read_csv("customers.csv")
        df = df.set_index("ID")
        
        self.nodes = []
        
        # !!! TRY REPLACING WITH MAP FUNCTION
        source = True
        for customer_id,data in df.iteritems():
            if source:
                source_location = [scale * int(data[0]), scale * int(data[1])]
                self.nodes.append(Source(source_location))
                source = False
            else:
                location = [scale * int(data[0]), scale * int(data[1])]
                power_demand = data[2:].tolist()
                self.nodes.append(Node(location, power_demand, customer_id))
                
    # def __init__(self, nominal_voltage):
        
    #     self.Vnom = nominal_voltage
    
    # def import_customers(self, scale=1):
        
    #     # import customer profiles from CSV "customers.csv"
        
    #     # pandas.DataFrame populated with data from customers.csv
    #     df = pd.read_csv("customers.csv")
    #     # treat first column as index
    #     df = df.set_index("ID")
        
    #     self.nodes = []
        
    #     # for each customer create a node
    #     for customer_id,data in df.iteritems():
            
    #         # get customer (node) location scaled accordingly
    #         # index 0 -> X, index 1 -> Y
    #         loc = [scale * int(data[0]), scale * int(data[1])]
    #         # get customer power demand
    #         power_demand = data[2:].tolist()
    #         # create customer node with location, power demand and customer id
    #         self.nodes.append(Node(loc,power_demand,customer_id))
        
    #     # first node is source
    #     self.nodes[0].source = True
    
    # def check_source(self):
    #     """
    #     Checks if a source is present
    #     """
    #     found = False
    #     for node in self.nodes:
    #         if node.customer_id.lower() in ["source","src","generation point"]:
    #             node.source = True
    #             found = True
    #             break
        
    #     if found == False:
    #         self.nodes[0].customer_id = "SOURCE"
    #         self.nodes[0].source = True

    # def cable_specs(self, resistance_unit_length, current_rating, cost_unit_length):
    #     # !!! future: add similar import to customers for cables
        
    #     self.res_l = resistance_unit_length
    #     self.Imax = current_rating
    #     self.cost_l = cost_unit_length
        
    
"""
TESTING AREA
"""

n = NetworkDesigner()
n.import_customers()