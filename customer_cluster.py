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
        Customer object for clustering algorithm.

        Parameters
        ----------
        customer_id : string, int or float
            ID for customer.
        position : array_like
            X and Y coordinates of customer in 2D. Shape 2x1.
        power_demand : array_like
            Hourly power demand of customer. 1D array.

        """
        
        self.customer_id = customer_id
        self.position = tuple(position)
        self.Pdem = np.array(power_demand)


class Cluster:
    
    def __init__(self,position,customers):
        """
        Cluster object which contains Customer objects.

        Parameters
        ----------
        position : array_like
            X and Y coordinates of cluster centroid in 2D. Shape 2x1.
        customers : array_like
            Array of Customer objects.

        """
        
        self.position = tuple(position)
        self.customers = list(customers)
        self.n_customers = len(customers)
        self.distances = self._dist_matrix()  # calculate distance matrix
        

        self.Pdem_total = 0
        for customer in self.customers:
            self.Pdem_total += customer.Pdem
        
        self.valid = False
        
    def _dist_matrix(self):
        """
        Creates array populated with distances between customers and centroid
        of cluster. Array is 1D, shape 1 x len(customers).

        Returns
        -------
        Numpy array
            Array populated with internal centroid-customer distances.

        """

        # x and y coordinates of all customers
        X = np.array([customer.position[0] for customer in self.customers])
        Y = np.array([customer.position[1] for customer in self.customers])
        
        # x and y of centroid
        X_c = self.position[0]
        Y_c = self.position[1]
        
        # euclidian distance
        return ((X_c - X)**2 + (Y_c - Y)**2)**(0.5)
    
    def test_distances(self,max_distance):
        """
        Checks if distances between centroid and customers is valid.
        Affects validity of cluster.

        Parameters
        ----------
        max_distance : float
            Maximum distance allowed between centroid and customers.

        Returns
        -------
        None.

        """
        
        if np.max(self.distances) > max_distance:
            self.valid = False
            
            print("\ndistance constraint broken")
            
        else:
            self.valid = True
            
            print("\ndistance valid")
    
    def test_voltages(self,network_voltage,max_voltage_drop,res_per_meter):
        """
        Tests if voltage drops valid in lines connecting centroid and
        customers. Affects validity of cluster.

        Parameters
        ----------
        network_voltage : float
            Voltage at which network operates.
        max_voltage_drop : TYPE
            Maximum allowable voltage drop within clusters.
        res_per_meter : TYPE
            Cable's resistance per meter (ohm/m).

        Returns
        -------
        None.

        """
        
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
        """
        Checks if number of connections below maximum allowed. Affects
        validity of cluster.

        Parameters
        ----------
        max_connections : int
            Maximum connections (or customers) allowed per cluster.

        Returns
        -------
        None.

        """
        
        if len(self.customers) > max_connections:
            
            self.valid = False
            
            print("\ncluster max connections constraint broken")
            
        else:
            
            print("\ncluster max connections valid")
            pass


class InitCluster(Cluster):
    
    def __init__(self,customers):
        """
        Special cluster object used for first cluster created.
        Centroid is automatically calculated at creation, instead of
        being set as a parameter.

        Parameters
        ----------
        customers : array-like
            Array of Customer objects.

        Returns
        -------
        None.

        """
        
        self.customers = list(customers)
        self.n_customers = len(customers)
        self._find_centroid()
        self.distances = self._dist_matrix()  # inherited from Cluster
        self.valid = False
        
    def _find_centroid(self):
        """
        Find centroid of cluster.
        """
        
        # x and y coordinates of all customers
        X = [customer.position[0] for customer in self.customers]
        Y = [customer.position[1] for customer in self.customers]
        
        # x and y coordinates of centroid
        self.position = (sum(X) / len(self.customers),
                         sum(Y) / len(self.customers))