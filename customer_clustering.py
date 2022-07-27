# -*- coding: utf-8 -*-
"""

    Customer Clustering
    
    "Energy For Development" VIP (University of Strathclyde)
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

import customer_cluster as cc

class CustomerClustering:
    
    def __init__(self, init_cluster, max_connections, network_voltage,
                 pole_cost, resistance_per_km, current_rating, cost_per_km,
                 max_voltage_drop=None, max_distance=None):
        
        # network parameters
        self.network_voltage = network_voltage
        if max_voltage_drop == None:
            # if none specified, take as 6% of network voltage
            self.max_votlage_drop = 0.06 * network_voltage
        else:
            self.max_voltage_drop = max_voltage_drop
        
        # pole parameters
        self.max_distance = max_distance
        self.max_connections = max_connections
        self.pole_cost = pole_cost
        
        # cable parameters
        self.res_m = resistance_per_km / 1000
        self.current_rating = current_rating
        self.cost_m = cost_per_km / 1000
        
        # initialise clusters array
        self.clusters = [init_cluster]
        
        self.all_clusters_valid = False
        
    @classmethod
    def import_from_csv(cls, filename, max_connections,
                        network_voltage, pole_cost, resistance_per_km,
                        current_rating, cost_per_km, scale_factor=1,
                        max_voltage_drop=None, max_distance=None):
        
        # read csv file as pandas dataframe
        df = pd.read_csv("nodes.csv")
        df = df.set_index("ID")
        
        # import customers and create initial single cluster
        customers = []
        for customer_id,data in df.iteritems():
            position = (scale_factor*data[0], scale_factor*data[1])  # X 0, Y 1
            power_demand = data[2:]
            customers.append(cc.Customer(customer_id,position,power_demand))
        
        init_cluster = cc.InitCluster(customers)
        
        return cls(init_cluster, max_connections, network_voltage, pole_cost,
                   resistance_per_km, current_rating, cost_per_km,
                   max_voltage_drop=max_voltage_drop,
                   max_distance=max_distance)
    
    @classmethod
    def import_from_OTHER(cls):
        
        # PLACEHOLDER
        pass
    
    def cluster(self):
        
        while self.all_clusters_valid == False:
            
            # test constraints on all clusters
            self._test_constraints()  # updates value of all_clusters_valid
            
            # keep valid and apply kmeans (k=2) to invalid clusters
            new_clusters = []
            for cluster in self.clusters:
                if cluster.valid == True:  # keep valid clusters
                    new_clusters.append(cluster)
                elif cluster.valid == False:
                    new_clusters += self._apply_kmeans(cluster)
                    # self._apply_kmeans(cluster)
            
            self.clusters = new_clusters
            
    def _test_constraints(self):
        
        self.all_clusters_valid = True  # assume all clusters valid initially
        
        for cluster in self.clusters:
            
            cluster.valid = True  # assume cluster valid initially
            
            # test constraints - these methods update cluster.valid
            if self.max_distance != None:  # if max distance specified
                cluster.test_distances()
            cluster.test_voltages(self.network_voltage,self.max_voltage_drop,
                                  self.res_m)
            cluster.test_max_connections(self.max_connections)
            
            if cluster.valid == False:
                self.all_clusters_valid = False
                
    def _apply_kmeans(self,cluster):
        # split invalid cluster into two new clusters
        
        pos = np.array([customer.position for customer in cluster.customers])
        
        kmeans = KMeans(n_clusters=2).fit(pos)  # apply kmeans to invalid
        cluster_centers = kmeans.cluster_centers_
        cust_labels = kmeans.labels_
        
        new_clusters = []
        
        for ce_label, center in enumerate(cluster_centers):
            customers = []
            for cu_idx, customer in enumerate(cluster.customers):
                # if customer label = centroid label
                if cust_labels[cu_idx] == ce_label:
                    customers.append(customer)
            
            # create new cluster
            new_clusters.append(cc.Cluster(center,customers))
            
        return new_clusters