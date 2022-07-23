# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 22:51:26 2022

@author: fredo
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


class Customer:
    
    def __init__(self,customer_id,location,power_demand):
        
        self.customer_id = customer_id
        self.location = tuple(location)
        self.Pdem = np.array(power_demand)
        
        self.I = np.zeros((len(power_demand), len(power_demand)))
    
        
class Cluster:
    
    def __init__(self,location,nodes):
        
        self.location = location
        self.nodes = nodes  # list of nodes (1D array)
        self.total_Pdem = np.sum([node.Pdem for node in self.nodes])
        
        self.dist_csrt = False
        self.max_node_csrt = False


class CustomerClusterer:
    
    def __init__(self,pole_max_customers):
        
        self.max_cust = pole_max_customers  # maximum customers per pole
        self.clusters = []  # initialise clusters list
    
    def network_specs(self,network_voltage, max_voltage_drop=None):
        
        self.Vnet = network_voltage  # base operating voltage of network
        
        # if maximum voltage drop not specified, take as 6% of network voltage
        if max_voltage_drop is None:
            self.Vdrop_max = 0.06 * self.Vnet
        else:
            self.Vdrop_max = max_voltage_drop
    
    def cable_specs(self, res_per_km, max_current, cost_per_km):
        
        self.res_meter = res_per_km / 1000
        self.Imax = max_current
        self.cost_meter = cost_per_km / 1000
    
    def customers_from_csv(self, file_name):
        
        # read CSV file
        df = pd.read_csv(str(file_name))
        df = df.set_index("ID")
        
        init_customers = []
        
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
                init_customers.append(
                    Customer(customer_id,location,power_demand)
                    )
        
        # calculate current drawn by each customer
        for customer in init_customers:
            customer.I = customer.Pdem / customer.Vnet
        
        # create first cluster
        self.clusters.append(Cluster(init_customers))
        
    def IMPORT_FROM_OTHER(self):
        
        # PLACEHOLDERS
        pass
    
    # METHODS FOR CLUSTERING
    
    def apply_kmeans(self,cluster,k=2):
        
        positions = np.array([node.location for node in cluster.nodes])
        kmeans = KMeans(n_clusters=k).fit(positions)
        
        # retrieve centroids and node labels
        # create new clusters with respective data
        
        # zip together nodes and respective labels
        labels = kmeans.labels_.tolist()
        labels_nodes = zip(labels, cluster.nodes)
        
        new_clusters = []
        centroids = kmeans.cluster_centers_.tolist()
        for idx_c, centroid_location in enumerate(centroids):
            
           # label of node = index of centroid
           nodes = [label_node[1] for label_node in labels_nodes 
                    if label_node[0] == idx_c]
           
           new_clusters.append(Cluster(centroid_location, nodes))
        
        return new_clusters  # return list of newly created clusters
    
    def cluster(self):
        
        dist_csrt = False
        while dist_csrt == False:
            
            # apply k=2 kmeans on clusters with broken dist csrt
            for idx,cluster in enumerate(self.clusters):
                
                if cluster.dist_csrt == False:  # if cluster dist csrt broken
                    
                    # apply kmeans
                    # remember index of "bad" cluster
                    # add new clusters to list of "fresh" clusters
                    pass
                
                elif cluster.dist_csrt == True:
                    
                    # do nothing
                    pass
                
            # update the cluster list (remove "bad" add "fresh")
            
            # test distance constraints on clusters
            
    
    
    
    
    