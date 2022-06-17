# -*- coding: utf-8 -*-
"""

    Network Designer for "Energy 4 Development" VIP
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    Based on MATLAB code by Steven Nolan ( )

"""

class networkDesigner:
    """
    
    Main class that houses algorithm.
    
    Manages inter-node methods.
    
    Parameters
    ----------
    num_nodes : int
        Number of nodes present in network.
    positions : list-like object
        X & Y coordinate pairs for position of each node.
    
    """
    
    def __init__(self, num_nodes, positions, scale):
        
        # number of nodes in network
        # includes source node (node 0 aka "SRC")
        self.num_nodes = num_nodes
        
        # base length for distances
        self.scale = scale
        
        
        
        pass 
        
class Node:
    """
    
    needs:
        
    position
    name
    parent node indicator (can be string of parent node name)
    current matrix/list from hour 0 to 8760
    voltage //
    current status (calculated or not)
    voltage //
    
    connection matrix? (list of nodes connected to, )
    
    """
    
    def __init__(self):
        pass
    