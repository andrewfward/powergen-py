# -*- coding: utf-8 -*-
"""

    Customer Clustering
    
    "Energy For Development" VIP (University of Strathclyde)
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


class CustomerClustering:
    
    def __init__(max_connections, network_voltage, pole_cost
                 resistance_per_km, current_rating, cost_per_km,
                 max_voltage_drop=None, max_distance = None):
        
        # network parameters
        self.max_connections = max_connections
        self.network_voltage = network_voltage
        
        # pole parameters
        self.pole_cost = pole_cost
        
        # cable parameters
        self.res_m = resistance_per_km / 1000
        self.current_rating = current_rating
        self.cost_m = cost_per_km / 1000
        
    
    @classmethod
    def import_from_csv(cls, filename, max_connections,
                        network_voltage, pole_cost, resistance_per_km,
                        current_rating, cost_per_km,
                        max_voltage_drop=None, max_distance = None)
    
    