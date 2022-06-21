# -*- coding: utf-8 -*-
"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""

import pandas as pd

class Node:
    
    def __init__(self, location, power_demand, customer_id):
        
        # location is tuple with X-Y coordinates
        self.location = location
        
        # power demand is list-like object
        self.pdem = power_demand
        
        # customer ID displayed in final plot
        self.customer_id = customer_id
        
        # status indicators for constraints check
        self.current_calculated = False
        self.voltage_calculated = True
        
        if self.customer_id.lower() in ["src","source"]:
            self.source = True

class NetworkDesigner:
    
    def __init__(self, nominal_voltage):
        
        self.Vnom = nominal_voltage
    
    def import_customers(self, scale=1):
        
        # import customer profiles from CSV "customers.csv"
        
        # pandas.DataFrame populated with data from customers.csv
        df = pd.read_csv("customers.csv")
        # treat first column as index
        df = df.set_index("ID")
        
        self.nodes = []
        for customer_id,data in df.iteritems():
            
            # get customer (node) location scaled accordingly
            # index 0 -> X, index 1 -> Y
            loc = (scale * int(data[0]), scale * int(data[1]))
            # get customer power demand
            power_demand = data[2:].tolist()
            # create customer node with location, power demand and customer id
            self.nodes.append(Node(loc,power_demand,customer_id))
    
    def check_source(self):
        for n in self.nodes:
            
    
    def cable_specs(self, resistance_unit_length, current_rating, cost_unit_length):
        # !!! future: add similar import to customers for cables
        
        self.res_l = resistance_unit_length
        self.Imax = current_rating
        self.cost_l = cost_unit_length
        
    
"""
TESTING AREA
"""

n = NetworkDesigner(240)
n.import_customers()