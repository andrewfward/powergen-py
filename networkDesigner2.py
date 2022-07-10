"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""

import pandas as pd
import numpy as np

class Source:
    
    node_id = "SOURCE"
    
    def __init__(self, location):
        
        # location is tuple --> [0] is X, [1] is Y
        self.loc = location


class Node:
    
    def __init__(self, location, node_id, power_demand):
        
        # location is tuple --> [0] is X, [1] is Y
        self.loc = tuple(location)
        
        self.node_id = str(node_id)
        
        self.Pdem = power_demand
        
        self.cost = 0
        
        # initially constraints considered as satisfied
        self.csrt_sat = True
        
        #-------CONNECTIONS--------------------#
        
        # all nodes are initially connected to the source
        self.parent = 0
        
        self.children = []
        
        # resistance between itself and parent node (upstream)
        self.line_res = 0
        
        #-------CURRENT/VOLTAGE TRACKERS-------#
        
        # current drawn by node at each time step
        self.I = [0]*len(power_demand)
        
        # current in line between itself and parent node (upstream) at each time step
        self.I_line = [0]*len(power_demand)
        
        # voltage across node at each time step
        self.V = [0]*len(power_demand)
        
        #-------CMST TRACKERS------------------#
        
        self.V_checked = False
        self.I_checked = False
        
        pass
    
    def isgate(self):
        """
        True if node is gate node (connected to source node).
        False otherwise.
        
        """
        pass


class NetworkDesigner:
    
    def __init__(self, network_voltage, max_V_drop=None):
        
        # base operating voltage of network
        self.Vnet = network_voltage
        
        # if maximum voltage drop not specified, take as 6% of network voltage
        if max_V_drop == None:
            self.Vdrop_max = 0.06 * self.Vnet
        else:
            self.Vdrop_max = max_V_drop
        
        pass
    
    def import_nodes_kml(self,scale_factor=1):
        
        # TO BE IMPLEMENTED
        
        pass
    
    def import_nodes_csv(self,scale_factor=1):
        
        scale = scale_factor
        
        df = pd.read_csv("nodes.csv")
        df = df.set_index("ID")
        
        self.nodes = []
        
        source = True
        for node_id,data in df.iteritems():
            # first entry is source
            if source:
                source_location = [scale * int(data[0]), scale * int(data[1])]
                self.nodes.append(Source(source_location))
                source = False
            # rest are nodes
            else:
                location = [scale * int(data[0]), scale * int(data[1])]
                power_demand = data[2:].tolist()
                self.nodes.append(Node(location, node_id, power_demand))
    
    def cable_specs(self, res_per_km, max_current, cost_per_km):
        
        self.res_meter = res_per_km / 1000
        
        self.Imax = max_current
        
        self.cost_meter = cost_per_km / 1000
    
    def _init_subtrees(self):
        
        for index, node in enumerate(self.nodes):
            if type(node) == Source:
                continue
            else:
                node.subtree = index
    
    def _init_matrices(self):
        """
        Create connection/distance/resistanece/checked paths matrices. Uses numpy arrays.
        
        """
        
        # square matrices size of nodes array
        size = (len(self.nodes), len(self.nodes))
        
        # create DISTANCE MATRIX
        self.distances = np.zeros(size)
        
        # populate distance matrix
        for i, node1 in enumerate(self.nodes):
            
            x1 = node1.loc[0]
            y1 = node1.loc[1]
            
            for j, node2 in enumerate(self.nodes):
                
                x2 = node2.loc[0]
                y2 = node2.loc[1]
                
                # euclidean distance = sqrt((y2-y1)^2 - (x2-x1)^2)
                distance = ((y2-y1)**2 + (x2-x1)**2)**(1/2)
                
                self.distances[i,j] = distance
        
        # create CONNECTION MATRIX
        self.connections = np.zeros(size)
        
        # populate connection matrix
        self.connections[0,:] = self.distances[0,:]
        self.connections[:,0] = self.distances[:,0]
        
        # create PATHS CHECKED MATRIX
        # paths between any node and itself set as checked
        self.path_checked = np.eye(size[0], dtype=bool)
    
    def calculate_res(self,node):
        """
        Calculates the resistance between a node and its parent.
        
        """
        if type(node) == Node:
            node_index = self.nodes.index(node)
            parent_index = node.parent
            
            node.line_res = self.res_meter * self.distances[node_index,parent_index]
        
        # if source passed
        else:
            pass
    
    def _init_constraints(self):
        """
        Initial constraints test before Esau-Williams algorithm is applied.
        
        """

        for node in self.nodes:
            
            if type(node) == Node:
                
                # calculate resistance between each node and respective parent
                self.calculate_res(node)
                
                # I(t) = Pdem(t) / Vnet         (DC current)
                I = [(Pdem/self.Vnet) for Pdem in node.Pdem]
                
                # if voltage drop across connection line above maximum allowable
                if max(I) * node.line_res > self.Vdrop_max:
                    
                    # node breaks constraint
                    node.csrt_sat = False
                
                else:
                    node.csrt_sat = True
            
            else:
                pass
                

    def setup(self):
        """
        Initialisation phase for CMST
        
        """
        # all nodes part of own subtree initially
        self._init_subtrees()
        
        self._init_matrices()
        
        self._init_constraints()
        
        pass
    
    def cmst(self):
        
        pass
    
    def output(self):
        
        pass
    
    def build_network(self):
        
        pass