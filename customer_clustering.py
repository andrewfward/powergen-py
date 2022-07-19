# -*- coding: utf-8 -*-
"""

    Customer Clustering for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)

"""

import numpy as np
import pandas as pd
import k_means_constrained as kms

class Customer:
    
    def __init__(self,customer_id,location,power_demand):
        
        self.customer_id = customer_id
        self.location = location
        self.Pdem = power_demand
        
    def assign_label(self,label):
        # assigns pole label to customer
        
        self.label = label


class Pole:
    
    def __init__(self):
        
        pass

class CustomerClustering:
    
    def __init__(self, pole_max_customers, pole_min_customers):
        
        self.size_max = pole_max_customers
        self.size_min = pole_min_customers
    
    def customers_from_csv(self, file_name):
        
        # read CSV file
        df = pd.read_csv(str(file_name))
        df = df.set_index("ID")
        
        self.customers = []
        
        # retrieve customers from CSV file
        source = True
        for customer_id,data in df.iteritems():
            # first entry is source
            if source:
                continue
            # rest are nodes
            else:
                location = (data[0], data[1])
                power_demand = data[2:].tolist()
                self.customers.append(
                    Customer(customer_id,location,power_demand)
                    )
                
    def             
                
                
                
    