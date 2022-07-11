"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""

import pandas as pd
import numpy as np
import sys


class Source:
    
    node_id = "SOURCE"
    
    def __init__(self, location):
        
        self.loc = tuple(location)  # [0] is X, [1] is Y
    
    def isgate(self):
        
        return False


class Node:
    
    def __init__(self, location, node_id, power_demand):
        
        self.loc = tuple(location)  # [0] is X, [1] is Y
        
        self.node_id = str(node_id)
        
        self.Pdem = power_demand
        
        self.cost = 0
        
        self.csrt_sat = True  # constraints satisfied upon creation
        
        #-------CONNECTIONS---------------------------------------------------#
        
        self.parent = 0  # all nodes initially connected to source
        
        self.children = []
        
        self.line_res = 0  # resistance in line between node and its parent
        
        #-------CURRENT/VOLTAGE TRACKERS--------------------------------------#
        
        self.I = [0]*len(power_demand)  # current drawn by node at each hour
        
        self.I_line = [0]*len(power_demand)  # current in line at each hour
        
        self.V = [0]*len(power_demand)  # voltage across node at each time step
        
        #-------CMST TRACKERS-------------------------------------------------#
        
        self.V_checked = False
        self.I_checked = False
    
    def isgate(self):
        """
        True if node is gate node (connected to source node).
        False otherwise.
        
        """
        
        if self.parent == 0:
            return True
        else:
            return False


class NetworkDesigner:
    
    def __init__(self, network_voltage, max_V_drop=None):
        
        # base operating voltage of network
        self.Vnet = network_voltage
        
        # if maximum voltage drop not specified, take as 6% of network voltage
        if max_V_drop is None:
            self.Vdrop_max = 0.06 * self.Vnet
        else:
            self.Vdrop_max = max_V_drop
    
    def import_nodes_kml(self,scale_factor=1):
        
        # TO BE IMPLEMENTED
        
        pass
    
    def import_nodes_csv(self,scale_factor=1):
        
        scale = scale_factor
        
        # read CSV file
        df = pd.read_csv("nodes.csv")
        df = df.set_index("ID")
        
        self.nodes = []
        
        # create source and node objects from entries in CSV
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
    
    #-------INITIALISATION PHASE----------------------------------------------#
    
    def _init_subtrees(self):
        """
        Sets the subtree of each node to iteself. Only used in initialisation
        phase for Esau-Williams algorithm.

        Returns
        -------
        None.

        """
        
        for index, node in enumerate(self.nodes):
            if type(node) == Source:
                continue
            else:
                node.subtree = index
    
    def _init_matrices(self):
        """
        Create connection/distance/resistanece/checked paths matrices.
        Uses numpy arrays.
        
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
            node_idx = self.nodes.index(node)  # node's index
            parent_idx = node.parent           # node's parent's index
            
            # line resistance = res/m * distance
            node.line_res = (self.res_meter
                            * self.distances[node_idx,parent_idx])
        
        # if source passed
        else:
            pass
    
    def _init_constraints(self):
        """
        Initial constraints test before Esau-Williams algorithm is applied.
        Tests if voltage drops across connections are acceptable.
        
        """

        for node in self.nodes:
            
            if type(node) == Node:
                
                # calculate resistance between each node and respective parent
                self.calculate_res(node)
                
                # I(t) = Pdem(t) / Vnet         (DC current)
                currents = ((Pdem/self.Vnet) for Pdem in node.Pdem)
                
                for current in currents:
                    
                    # if voltage drop too high constraint broken
                    if (current * node.line_res) > self.Vdrop_max:
                        node.csrt_sat = False
                    # if voltage drop acceptable constraint satisfied
                    else:
                        node.csrt_sat = True
            
            # skip if source object passed
            else:
                pass
    
    #-------CMST METHODS------------------------------------------------------#
    
    def _candidate_nodes(self):
        # RETURN INDICES OF GATE & NODE
        
        # filter out gate nodes (nodes connected to source)
        gates = filter(lambda node: node.isgate() == True, self.nodes)
        
        best_tradeoff = 0        
        for gate in gates:
            
            gate_idx = self.nodes.index(gate)  # gate index in nodes array
            
            distance_gate_src = self.distances[gate_idx,0]  # source index = 0
            min_distance = distance_gate_src
            
            for node_idx,node in enumerate(self.nodes):
                # skip node if:
                    # source
                    # is gate in question
                    # already connected to gate
                    # part of same subtree as gate
                    # path has been checked
                
                if type(node) == Source:
                    continue
                
                elif (gate_idx != node_idx
                    and gate.subtree != node.subtree
                    and self.path_checked[gate_idx, node_idx] == False
                    and self.connections[gate_idx, node_idx] == 0):
                
                    # if distance gate-node lowest so far, update min distance
                    if self.distances[gate_idx,node_idx] < min_distance:
                        
                        min_distance = self.distances[gate_idx,node_idx]
                        best_node_idx = node_idx
                        
            # trade-off = distance(gate,src) - distance(gate,node)
            tradeoff = distance_gate_src - min_distance
            
            if tradeoff > best_tradeoff:
                best_tradeoff = tradeoff
                best_gate_idx = gate_idx
                
                print("\nnew tradeoff:",tradeoff)
                print("gate:", best_gate_idx)
                print("node:", best_node_idx)
        
        print("\nFINAL RESULTS")
        print("gate: ", best_gate_idx)
        print("node: ", best_node_idx)
        print("tradeoff: ", best_tradeoff)
        
        return best_gate_idx, best_node_idx
        
    #-------HIGH LEVEL METHODS------------------------------------------------#
    
    def setup(self):
        """
        Initialisation phase for CMST.
        Step 1: assign each node to own subtree
        Step 2: create distance, connection, checked paths matrices
        Step 3: test voltage constraints of initial connections
                > calculate resistance of connections
        
        """
        # all nodes part of own subtree initially
        self._init_subtrees()
        
        # create & populate connection/distance/checked path matrices
        self._init_matrices()
        
        # calculate resistance of line between nodes and source
        # and test voltage constraints
        self._init_constraints()
    
    def cmst(self):
        
        further_improvements = True
        
        while further_improvements == True:
            
            # find candidate pair
            
            # connect pair & test constraints (I & V)
            
            # if constraint broken:
                # undo connection & mark path as checked
            
            # if constraint satisfied:
                # keep connection & mark path as checked
        
            pass
    
    def output(self):
        
        pass
    
    def build_network(self):
        
        pass