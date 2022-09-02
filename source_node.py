# -*- coding: utf-8 -*-
"""

    Source and Node classes for Network Designer
    
    "Energy For Development" VIP (University of Strathclyde)
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
"""

import numpy as np


class Source:
    
    node_id = "SOURCE"
    
    def __init__(self, location):
        """
        Source node, purely used to store network source location.

        Parameters
        ----------
        location : array-like
            1x2 array containing X and Y coordinates of source.

        """
        
        self.loc = tuple(location)  # [0] is X, [1] is Y
    
    def isgate(self):
        
        return False


class Node:
    
    def __init__(self, location, power_demand, node_id=None):
        """
        Represents any element in the network that draws power, such
        as customers and clusters of customers.

        Parameters
        ----------
        location : array-like
            1x2 array containing X and Y coordinates of source.
        power_demand : array-like
            Power demand of node.
        node_id : str, optional
            Node identifier. The default is None.

        """
        
        self.loc = tuple(location)  # [0] is X, [1] is Y
        self.node_id = str(node_id)
        self.Pdem = np.array(power_demand, dtype="float64")
        self.cost = 0
        self.csrt_sat = True  # constraints satisfied upon creation
        
        #-------CONNECTIONS---------------------------------------------------#
        
        self.parent = 0  # all nodes initially connected to source
        self.children = []
        self.line_res = 0  # resistance in line between node and its parent
        
        #-------CURRENT/VOLTAGE ARRAYS----------------------------------------#
        
        self.I = 0  # current drawn by node at each hour
        self.I_line = 0  # current in line at each hour
        self.V = 0  # voltage across node at each time step
        
        #-------CMST TRACKERS-------------------------------------------------#
        
        self.V_checked = False
        self.I_checked = False
    
    def isgate(self):
        """
        Returns gate status of node.

        Returns
        -------
        bool
            True if node is gate node. False otherwise.

        """
        
        if self.parent == 0:
            return True
        else:
            return False
    
    def has_children(self):
        """
        Returns parent status of node.

        Returns
        -------
        bool
            True if node has children. False otherwise.

        """
        
        if self.children != []:
            return True
        
        else:
            return False