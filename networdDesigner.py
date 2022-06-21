# -*- coding: utf-8 -*-
"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""

class networkDesigner:
    
    def __init__(self, num_nodes, positions, scale, Vnom, Imax, resistance, cost):
        
        # number of nodes in network
        # includes source node (node 0 aka "SRC")
        self.num_nodes = num_nodes
        
        # position of nodes in x-y plane (list-type)
        self.positions = positions
        
        # base length for distances
        self.scale = scale
        
        # mini-grid nominal voltage
        self.nom_volt = Vnom
        
        # cable current rating
        self.current_rating = Imax
        
        # cable resistance per unit length (ohm/km)
        self.res = resistance
        
        # cost per unit length (£/km)
        self.cost = cost
        
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
    