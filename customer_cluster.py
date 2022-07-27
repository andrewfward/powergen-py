# -*- coding: utf-8 -*-
"""

    Customer and Cluster classes for Customer Clustering
    
    "Energy For Development" VIP (University of Strathclyde)
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
"""

import numpy as np

class Customer:
    
    def __init__(self,customer_id,position,power_demand):
        """
        

        Parameters
        ----------
        customer_id : string, int or float
            ID for customer.
        position : array_like
            X and Y coordinates of customer in 2D. Shape 2x1.
        power_demand : array_like
            Hourly power demand of customer. 1D array.

        Returns
        -------
        None.

        """
        self.customer_id = customer_id
        self.position = tuple(position)
        self.Pdem = np.array(power_demand)


class Cluster:
    
    def __init__(self,position,customers):
        """
        

        Parameters
        ----------
        position : array_like
            X and Y coordinates of cluster centroid in 2D. Shape 2x1.
        customers : array_like
            Array of Customer objects (preferably list).

        Returns
        -------
        None.

        """
        self.position = tuple(position)
        self.customers = customers
        self.distances = self._dist_matrix()  # calculate distance matrix
        
        self.valid = False
        
    def _dist_matrix(self):
        """
        Creates array populated with distances between customers and centroid
        of cluster. Array is 1D, shape 1 x len(customers).

        Returns
        -------
        None.

        """
        
        # x and y coordinates of all customers
        X = np.array([customer.position[0] for customer in self.customers])
        Y = np.array([customer.position[1] for customer in self.customers])
        
        # x and y of centroid
        X_c = self.position[0]
        Y_c = self.position[1]
        
        # euclidian distance
        return ((X_c - X)**2 + (Y_c - Y)**2)**(1/2)
    
    def test_distances(self,max_distance):
        
        if np.max(self.distances) > max_distance:
            # self.distances_valid = False
            self.valid = False
            
            print("\ndistance constraint broken")
            
        else:
            # self.distances_valid = True
            self.valid = True
            
            print("\ndistance valid")
    
    def test_voltages(self,network_voltage,max_voltage_drop,res_per_meter):
        
        for idx,customer in enumerate(self.customers):
            
            Vdrops = ((customer.Pdem/network_voltage) * res_per_meter
                      * self.distances[idx])
            
            if np.max(Vdrops) > max_voltage_drop:
                # self.voltage_valid = False
                self.valid = False
                
                print("\ncustomer voltage constraint broken",idx)
                
                break
            else:
                
                print("\ncustomer voltage valid",idx)
                
                pass
    
    def test_max_connections(self,max_connections):
        
        if len(self.customers) > max_connections:
            
            self.valid = False
            
            print("\ncluster max connections constraint broken")
            
        else:
            
            print("\ncluster max connections valid")
            pass


class InitCluster(Cluster):
    
    def __init__(self,customers):
        
        self.customers = customers
        self._find_centroid()
        self.distances = self._dist_matrix()
        
        # self.voltages_valid = False
        self.valid = False
        
    def _find_centroid(self):
        
        # x and y coordinates of all customers
        X = [customer.position[0] for customer in self.customers]
        Y = [customer.position[1] for customer in self.customers]
        
        # x and y coordinates of centroid
        self.position = (sum(X) / len(self.customers),
                         sum(Y) / len(self.customers))