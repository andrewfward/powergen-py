"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""

import pandas as pd
import numpy as np
import copy


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
        
        self.Pdem = np.array(power_demand, dtype="float64")
        
        self.cost = 0
        
        self.csrt_sat = True  # constraints satisfied upon creation
        
        #-------CONNECTIONS---------------------------------------------------#
        
        self.parent = 0  # all nodes initially connected to source
        
        self.children = []
        
        self.line_res = 0  # resistance in line between node and its parent
        
        #-------CURRENT/VOLTAGE ARRAYS----------------------------------------#
        
        placeholder_array = np.zeros(len(self.Pdem))
        
        self.I = placeholder_array  # current drawn by node at each hour
        
        self.I_line = placeholder_array  # current in line at each hour
        
        self.V = placeholder_array  # voltage across node at each time step
        
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
    
    def has_children(self):
        """
        True if node has children. False otherwise.

        Returns
        -------
        bool
            Status of children existing.

        """
        
        if self.children != []:
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

        Parameters
        ----------
        node : Node
            Node object for which line resistance of upstream connection is
            calculated.

        Returns
        -------
        None.

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
                
                # calculate current drawn by node    I(t) = Pdem(t) / Vnet [DC]
                node.I = node.Pdem / self.Vnet

                # voltage drops is current * line resistance
                voltage_drops = node.line_res * node.I
                
                if np.max(voltage_drops) > self.Vdrop_max:
                    node.csrt_sat = False
                else:
                    node.csrt_sat = True

            else:
                pass
    
    #-------CMST METHODS------------------------------------------------------#
    
    def _candidate_nodes(self):
        
        best_tradeoff = 0
        best_gate_idx = None
        best_node_idx = None
        
        for gate in self.nodes:
            
            if type(gate) == Source:
                continue
            
            if gate.isgate() == False:
                continue
            
            gate_idx = self.nodes.index(gate)
            
            min_distance = self.distances[gate_idx,0]  # distance gate - SRC
            
            for node_idx, node in enumerate(self.nodes):
                
                if type(node) == Source:
                    continue
                
                if (self.path_checked[node_idx, gate_idx] == True
                    or self.path_checked[gate_idx,node_idx] == True
                    or node.subtree == gate.subtree
                    or node_idx in gate.children):
                    
                    continue
                
                elif self.distances[gate_idx,node_idx] == 0:
                    continue
                
                elif self.distances[gate_idx,node_idx] < min_distance:
                    
                    if self.connections[gate_idx,node_idx] == 0:
                        min_distance = self.distances[gate_idx,node_idx]
                        temp_best_node_idx = node_idx
                        temp_best_gate_idx = gate_idx
            
            tradeoff = self.distances[gate_idx,0] - min_distance
            
            if tradeoff > 0:
                if tradeoff > best_tradeoff:
                    best_tradeoff = tradeoff
                    best_gate_idx = temp_best_gate_idx
                    best_node_idx = temp_best_node_idx
        
        if type(best_gate_idx) == None or type(best_node_idx) == None:
            return False, False
        else:
            return best_gate_idx, best_node_idx
    
    # def _candidate_nodes(self):
    #     """
    #     Finds gate-node paid with best trade-off value for new connection.

    #     Returns
    #     -------
    #     best_gate_idx : int
    #         Index of gate with best trade-off value.
    #     best_node_idx : int
    #         Index of best node to join to.

    #     """
        
    #     # filter out gate nodes (nodes connected to source)
    #     gates = filter(lambda node: node.isgate() == True, self.nodes)
        
    #     best_tradeoff = 0        
    #     for gate in gates:
            
    #         gate_idx = self.nodes.index(gate)  # gate index in nodes array
            
    #         distance_gate_src = self.distances[gate_idx,0]  # source index = 0
    #         min_distance = distance_gate_src  # min distance initially SRC-gate
            
    #         for node_idx,node in enumerate(self.nodes):
    #             # skip node if:
    #                 # source
    #                 # is gate in question
    #                 # already connected to gate
    #                 # part of same subtree as gate
    #                 # path has been checked
                
    #             if type(node) == Source:
    #                 continue
                
    #             elif (gate_idx != node_idx
    #                 and gate.subtree != node.subtree
    #                 and self.path_checked[gate_idx, node_idx] == False
    #                 and self.connections[gate_idx, node_idx] == 0):
                
    #                 # if distance gate-node lowest so far, update min distance
    #                 if self.distances[gate_idx,node_idx] < min_distance:
                        
    #                     min_distance = self.distances[gate_idx,node_idx]
    #                     best_node_idx = node_idx
                
    #             else:
    #                 continue
                
    #         # trade-off = distance(gate,src) - distance(gate,node)
    #         tradeoff = distance_gate_src - min_distance
            
    #         if tradeoff > best_tradeoff and tradeoff > 0:
    #             best_tradeoff = tradeoff
    #             best_gate_idx = gate_idx
                
    #             # print("\nnew tradeoff:",tradeoff)
    #             # print("gate:", best_gate_idx)
    #             # print("node:", best_node_idx)
        
    #     # print("\nFINAL RESULTS")
    #     # print("gate: ", best_gate_idx)
    #     # print("node: ", best_node_idx)
    #     # print("tradeoff: ", best_tradeoff)
        
    #     return best_gate_idx, best_node_idx
    
    def _save_state(self):
        """
        Saves the network's current state.

        Returns
        -------
        None.

        """
        
        self.prev_nodes = copy.deepcopy(self.nodes)
        self.prev_connections = self.connections.copy()
        
    def _load_prev_state(self):
        
        self.nodes = self.prev_nodes
        self.connections = self.prev_connections
    
    def _connect_nodes(self, gate_idx, node_idx):
        """
        Connects a gate (node directly connected to source) with a specified
        node.

        Parameters
        ----------
        gate_idx : int
            Index of joining gate (in nodes array).
        node_idx : int
            Index of joining node (in nodes array).

        Returns
        -------
        None.

        """
        # get gate & node objects
        gate = self.nodes[gate_idx]
        node = self.nodes[node_idx]
        
        # mark path as checked
        self.path_checked[gate_idx,node_idx] = True
        self.path_checked[node_idx,gate_idx] = True        
        
        # mark connection in adjacency matrix
        distance = self.distances[gate_idx,node_idx]
        self.connections[gate_idx,node_idx] = distance
        self.connections[node_idx,gate_idx] = distance
        
        # update subtree for all nodes in gate subtree
        for subnode in self.nodes:
            if type(subnode) == Source:
                continue
            if subnode == node or subnode == gate:
                continue
            elif subnode.subtree == gate.subtree:
                
                print("updated subtree of " + str(subnode.node_id))
                print("old subtree: " + str(subnode.subtree))
                print("new subtree: " + str(node.subtree))
                
                subnode.subtree = node.subtree
            else:
                continue
        
        # update gate's subtree and parent
        gate.parent = node_idx
        gate.subtree = node.subtree
        
        node.children.append(gate_idx)  # mark gate as child of node
        
        # calculate line resistance of new connection
        # note: function calculates resistance of upstream connection, so
        #       passing in gate as argument because it is now downstream. 
        self.calculate_res(gate)
    
    def _reset_checks(self):
        
        for node in self.nodes:
            node.I_checked = False
            node.V_checked = False
    
    def _test_constraints(self,gate_idx):
        
        # 1 reset check variable of all nodes in network
        # 2 test current
        # 3 test voltage
        
        self._reset_checks()
        
        gate_node = self.nodes[gate_idx]  # get gate object
        
        print("\nchecking current")
        
        # set active node as connecting gate
        active_idx = gate_idx
        active_node = gate_node
        
        constraint_broken = False
        
        # test CURRENT
        while type(active_node) != Source and constraint_broken == False:
            
            # if active node has children:
            #   > ignore children with checked current
            #   > if child with unchecked current exists
            #       > child becomes active node
            
            all_checked = False
            
            # if active node has children
            if active_node.has_children() == True:
                
                # search for child with unchecked current
                for num, child_idx in enumerate(active_node.children):
                    child = self.nodes[child_idx]
                    
                    # child with unchecked current found, so stop searching
                    if child.I_checked == False:
                        active_idx = child_idx
                        active_node = child
                        break
                    
                    # all children have checked currents
                    elif (num + 1) == len(active_node.children):
                        all_checked = True
                    
                    else:
                        continue
            
            # if active node childless or all children have checked currents
            # we are at bottom of subtree
            if active_node.has_children() == False or all_checked == True:
                
                # current in line = current in child line + current node draws
                if active_node.has_children():
                    
                    I_line_children = 0
                    for child_idx in active_node.children:
                        I_line_children += self.nodes[child_idx].I_line
                    
                    active_node.I_line += active_node.I + I_line_children
                
                else:
                    active_node.I_line += active_node.I
                
                # check if current in line above maximum allowable
                if np.max(active_node.I_line) > self.Imax:
                    constraint_broken = True
                
                # mark node as checked
                active_node.I_checked = True
                
                # move upstream --> parent node becomes active node
                active_idx = active_node.parent
                active_node = self.nodes[active_idx]
        
        # test VOLTAGE
        
        print("\nchecking voltage")
        
        # set active node as gate of subtree
        active_idx = gate_node.subtree
        active_node = self.nodes[active_idx]
        
        while type(active_node) != Source and constraint_broken == False:
            
            # if voltage not checked then calculate voltage
            if active_node.V_checked == False:
                # if active node is gate of subtree
                if active_node.isgate() == True:
                    active_node.V = (self.Vnet
                                     - active_node.I_line 
                                     * active_node.line_res)
                    
                # if active node not gate of subtree
                else:
                    parent_node = self.nodes[active_node.parent]
                    active_node.V = (parent_node.V 
                                     - active_node.I_line 
                                     * active_node.line_res)
                
                active_node.V_checked = True
                
                # check constraint
                if np.min(active_node.V) < (self.Vnet - self.Vdrop_max):
                    constraint_broken = True
            
            elif active_node.V_checked == True:
                
                if active_node.has_children():
                    
                    for num, child_idx in enumerate(active_node.children):
                        child = self.nodes[child_idx]
                        
                        # child with unchecked voltage found, so stop searching
                        if child.V_checked == False:
                            active_idx = child_idx
                            active_node = child
                            break
                        
                        # all children have checked voltages, move upstream
                        elif (num + 1) == len(active_node.children):
                            active_idx = active_node.parent
                            active_node = self.nodes[active_idx]
                
                # active node is chidless, move upstream
                elif active_node.has_children() == False:
                    active_idx = active_node.parent
                    active_node = self.nodes[active_idx]
        
        if constraint_broken:
            return False
        
        else:
            
            print("\nCONNECTED:")
            print("gate " + str(gate_idx))
            print("node " + str(gate_node.parent))
            
            return True

    #-------HIGH LEVEL METHODS------------------------------------------------#
    
    def setup(self):
        """
        Initialisation phase for CMST.
        Step 1: assign each node to own subtree
        Step 2: create distance, connection, checked paths matrices
        Step 3: calculate current drawn by each node
        Step 4: calculate resistance of all connections
        Step 5: test voltage constraint on connection
        
        """
        # all nodes part of own subtree initially
        self._init_subtrees()
        
        # create & populate connection/distance/checked path matrices
        self._init_matrices()
        
        # calculate resistance of line between nodes and source
        # and test voltage constraints
        self._init_constraints()
        
        print("\nSETUP DONE!")
        
    def cmst(self):
        
        further_improvements = True
        self.old_best_gate = None
        self.old_best_node = None
        
        loop = 0
        
        while further_improvements == True: #and loop < 4:
            
            print("\nlooking for candidates")
            
            # find candidate pair
            best_gate_idx, best_node_idx = self._candidate_nodes()
            
            if best_gate_idx == False and best_node_idx == False:
                
                print("\nNEW CONNECTION NOT FOUND")
                break
            
            print("\nsaving state")
            
            # save current state before making connection
            self._save_state()
            
            print("\nconnecting nodes")
            print("ATTEMPTING")
            print("gate: " + str(best_gate_idx))
            print("node: " + str(best_node_idx))
            
            # connect pair
            self._connect_nodes(best_gate_idx, best_node_idx)
            
            print("\ntesting constraints")
            
            # test constraints on new connection
            # if constraint broken
            if self._test_constraints(best_gate_idx) == False:
                
                print("\nfailed constraints check, resetting connection")
                # reset the connection
                self._load_prev_state()
            
            # save best connections
            self.old_best_gate = best_gate_idx
            self.old_best_node = best_node_idx
            
            # further_improvements = False
            
            loop += 1
            print("\nloop " + str(loop))
    
    def output(self):
        
        pass
    
    def build_network(self):
        
        pass
    
    
    
    
    
    
#-------TEST LOGIC------------------------------------------------------------#
