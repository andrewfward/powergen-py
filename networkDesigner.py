# -*- coding: utf-8 -*-
"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""
"""
FUTURE WORK

- create (potentially external) function to extract info (location etc) directly from KML files.

"""
import pandas as pd
import numpy as np
from math import sqrt


class Node:
    
    def __init__(self, location, power_demand, customer_id):
        
        # customer ID displayed in final plot
        self.customer_id = str(customer_id)
        
        # location is tuple with X-Y coordinates
        self.loc = tuple(location)
        
        # power demand is list-like object
        self.Pdem = power_demand
        
        # voltage & current arrays
        self.volt = [0]*len(power_demand)
        self.curr = [0]*len(power_demand)
        
        # line resistance (between itself and parent node)
        self.res_line = 0
        
        # line current (between itself and parent node)
        self.curr_line = [0]*len(power_demand)

        # status indicators for constraints check
        self.current_calculated = False
        self.voltage_calculated = False
        
        # constraint checker (initially true)
        self.constraint_satisfied = True
        
        # index of gate node top of subtree
        # initially itself, set with __init_subtree method
        self.subtree = None
        
        # index of parent node
        # initially source node (index 0)
        self.parent = 0
        
        self.cost = 0
    
    def isgate(self):
        
        if self.parent == 0:
            return True


class Source:
    
    def __init__(self, location):
        
        self.customer_id = "SOURCE"
        
        self.loc = tuple(location)


class NetworkDesigner:
    
    def __init__(self, network_voltage):
        
        self.Vnet = network_voltage
        
        # attributes for CMST
        self.old_best_trade = None
        self.old_best_join = None
    
    def import_customers(self, scale=1):
        
        # !!! REPLACED WITH KML READER LATER
        
        df = pd.read_csv("customers.csv")
        df = df.set_index("ID")
        
        self.nodes = []
        
        # !!! TRY REPLACING WITH MAP FUNCTION
        source = True
        for customer_id,data in df.iteritems():
            # first entry is source
            if source:
                source_location = [scale * int(data[0]), scale * int(data[1])]
                self.nodes.append(Source(source_location))
                source = False
            # rest are nodes
            else:
                location = [scale * int(data[0]), scale * int(data[1])]
                power_demand = data[2:].tolist()
                self.nodes.append(Node(location, power_demand, customer_id))
    
    def _init_subtrees(self):
        """
        For initialisation phase only. Sets subtree of each node as node itself.
        
        """

        for index, node in enumerate(self.nodes):
            # source node excluded
            if type(node) == Source:
                pass
            else:
                node.subtree = index
    
    def _init_matrices(self):
        """
        For initialisation phase only. Creates adjacency, distance and checked path matrices for CMST.
        
        """

        size = (len(self.nodes), len(self.nodes))
        
        # initially no nodes connected to each other
        self.adj_matrix = np.zeros(size)
        # create distance matrix
        self.dist_matrix = np.zeros(size)
        # create path check matrix (paths between nodes and themselves set as checked (True))
        self.path_check_matrix = np.eye(size[0], dtype=bool)
        
        # populate distance matrix with distances
        # and connect all nodes to source
        for index1,node1 in enumerate(self.nodes):
            for index2,node2 in enumerate(self.nodes):
                x1 = node1.loc[0]
                y1 = node1.loc[1]
                
                x2 = node2.loc[0]
                y2 = node2.loc[1]
                
                distance = sqrt((y2-y1)**2 + (x2-x1)**2)
                
                self.dist_matrix[index1,index2] = distance
                
                # if calulcating the distance between source and node
                # connect them in adj matrix
                if type(node1) == Source or type(node2) == Source:
                    self.adj_matrix[index1,index2] = distance
                    
                    
    def cable_specs(self, resistance_per_km, current_rating, cost_per_km):
        # !!! future: add similar import to customers for cables
        
        # convert units to ohm per meter
        self.res_per_meter = resistance_per_km / 1000
        self.Imax = current_rating
        # convert untis to dollars per meter
        self.cost_per_meter = cost_per_km / 1000
    
    def calculate_resistance(self,node):
        # calculates resistance between node and parent node
        
        index_node = self.nodes.index(node)
        index_parent = node.parent
        node.res_line = self.res_per_meter * self.dist_matrix[index_node,index_parent]
    
    def _init_resistances(self):
        
        for node in self.nodes:
            if type(node) == Source:
                pass
            else:
                self.calculate_resistance(node)
    
    def _init_constraints(self):
        
        for node in self.nodes:
            if type(node) == Source:
                pass
            else:
                # current drawn by node at each time step (I = P/V)
                node.curr = [Pdem_t/self.Vnet for Pdem_t in node.Pdem]
                # drop across line connecting node and parent at each time step (Vdrop = R*I)
                line_Vdrop = [node.res_line * current for current in node.curr]
                # voltage at node at each time step (V = Vnet - Vdrop)
                node.volt = [self.Vnet - Vdrop for Vdrop in line_Vdrop]
                
                # check if voltage meets regulation
                if min(node.volt) < 0.94*self.Vnet:
                    node.constraint_satisfied = False
    
    def _tradeoff(self,index_gate,min_dist):
        """
        Calculates value for trade-off function for gate-node connection.    
        
        Trade-off = distance(source-gate) - minimum distance
        
        """
        
        return self.dist_matrix[index_gate,0] - min_dist 
        
        
    def _find_join(self):
        """
        Finds candidate nodes for new connection.

        Returns
        -------
        list
            Indexes of candidate nodes. Index 0 is gate node, Index 1 is other node.

        """
        # set up
        temp_tradeoff = 0
        tradeoff = 0
        
        
        # filter gate nodes
        gates = filter(lambda node: node.isgate() if type(node) == Node else False, self.nodes)
        for gate in gates:
            
            # gate node index (in nodes array)
            index_gate = self.nodes.index(gate)
            print(index_gate)
            
            # initially gate considered closest to source
            min_distance = self.dist_matrix[index_gate,0]
            
            for index_node, node in enumerate(self.nodes):
                
                # look for new minimum distance
                # EXCEPT: if node is gate itself, path already checked, node and gate connected, node is source
                if type(node) == Source:
                    continue
                elif index_node == index_gate or self.path_check_matrix[index_gate,index_node] or gate.subtree == node.subtree:
                    continue
                
                # if found node closer to gate than source
                elif self.dist_matrix[index_gate,index_node] < min_distance:
                    
                    # update minimum distance
                    min_distance = float(self.dist_matrix[index_gate,index_node])
                
                else:
                    continue
                
            # calculate temporary tradeoff function for node and gate connection
            temp_tradeoff = self._tradeoff(index_gate, min_distance)
            
            if temp_tradeoff > tradeoff and temp_tradeoff > 0:
                best_trade = index_gate
                best_join = index_node
                tradeoff = temp_tradeoff
                
                print("found new tradeoff",tradeoff)
                
        return [best_trade, best_join]
    
    def _check_join(self,node_pair):
        
        best_trade = node_pair[0]
        best_join = node_pair[1]
        
        # mark path between two nodes as checked
        self.path_check_matrix[best_trade, best_join] = True
        self.path_check_matrix[best_join, best_trade] = True
        
        # best trade (gate) node is now part of subtree of best join node
        self.nodes[best_trade].subtree = self.nodes[best_join].subtree
        
        # set parent of best trade to best join (connecting best trade to best join)
        self.nodes[best_trade].parent = best_join
        
        # if no further improvements
        if self.old_best_join == best_join and self.old_best_trade == best_trade:
            
            """
            CHANGE WHILE LOOP CONDITION TO FALSE
            """
            pass
        
        # disconnect best trade (gate) from source
        self.adj_matrix[best_trade,0] = 0
        self.adj_matrix[0,best_trade] = 0
        
        # connect best trade (gate) and best join
        distance = self.dist_matrix[best_trade,best_join]
        
        self.adj_matrix[best_trade,best_join] = distance
        self.adj_matrix[best_join,best_trade] = distance
        
        # calculate line resistance between best trade and best join
        # note: best join is parent of best trade
        self.calculate_resistance(self.nodes[best_trade])
        
    
    def build_network(self):
        """
        Builds network using Esau-Williams heuristic.
        
        """
        # INITIALISATION PHASE
        
        # !!! might want to make it external (program calls before .build_network())
        self.import_customers(scale=1)     # !!! scale factor goes here
        
        # set initial subtrees
        self._init_subtrees()
        # create adjacency / distance / path check matrices
        self._init_matrices()
        
        
        # INITIAL CONSTRAINT CHECK
        
        self._init_resistances()
        self._init_constraints()
        
        # CMST
        
        # Best trade = 1 (???)
        
        further_improvements = True
        while further_improvements:
            
            # find candidate gate and node for new connection
            connection_candidates = self._find_join()
            
            # test new connection
            self._check_join(connection_candidates)
            
            further_improvements = False

"""
TESTING AREA
"""

n = NetworkDesigner(240)
n.import_customers()
n.cable_specs(50,100,200)
n.build_network()