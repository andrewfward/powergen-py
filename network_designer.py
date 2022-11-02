# -*- coding: utf-8 -*-
"""

    Network Designer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( )

"""

import copy
import math

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

from source_node import Source, Node    


class NetworkDesigner:
    
    def __init__ (self, source_location, nodes_locations, nodes_power_dem,
                  network_voltage, pole_cost, pole_spacing, res_per_km,
                  max_current, cost_per_km, scl=1, max_V_drop=None,
                  node_ids=None, V_reg=6):
        """
        Generates network connecting nodes using Esau-Williams CMST.
        
        Parameters
        ----------
        source_location : array-like
            1x2 array containing X and Y coordinates of source.
        nodes_locations : array-like
            Array of 1x2 arrays containing X and Y coordinates of nodes.
        nodes_power_dem : array-like
            Array of arrays containing power demands of each
            node in network.
        network_voltage : float
            Operating voltage of network.
        pole_cost : float
            Cost of single electrical pole.
        pole_spacing : float
            Spacing between poles in meters.
        res_per_km : float
            Cable's resistance per kilometer (ohm/km).
        max_current : float
            Cable's maximum current rating.
        cost_per_km : float
            Cable's cost per km.
        scl : float, optional
            Scales coordinates of source and nodes by chosen amount.
            The default is 1.
        max_V_drop : flaot, optional
            Maximum voltage drop. If not specified value dictated by
            voltage regulation. The default is None.
        node_ids : array-like, optional
            Array containing node identifiers. The default is None.
        V_reg : float, optional
            Maximum voltage drop as percentage of network voltage.
            The default is 6.

        """
        
        #-------NODES & SOURCE------------------------------------------------#
        self.nodes = []
        
        # create source object
        self.nodes.append(Source(source_location))
        
        # create node objects
        for idx,loc in enumerate(nodes_locations):
            
            # get node ID
            if node_ids == None:  # if IDs NOT provided
                node_id = idx
            else:
                node_id = str(node_ids[idx])
            
            power_demand = nodes_power_dem[idx]
            self.nodes.append(Node(loc, power_demand, node_id=node_id))
        
        #-------NETWORK PARAMETERS--------------------------------------------#
        self.Vnet = network_voltage
        
        self.pole_cost = pole_cost
        self.pole_spacing = pole_spacing
        
        if max_V_drop is None:  # exact max voltage drop NOT specified
            self.Vdrop_max = V_reg/100 * self.Vnet
        else:
            self.Vdrop_max = max_V_drop
        
        #-------CABLE PARAMETERS----------------------------------------------#
        self.res_meter = res_per_km / 1000
        self.Imax = max_current
        self.cost_meter = cost_per_km / 1000
    
    @classmethod
    def import_from_csv(cls, filename, network_voltage, pole_cost, pole_spacing,
                        res_per_km, max_current, cost_per_km, scl=1,
                        max_V_drop=None, V_reg=6):
        """
        Imports source location and nodes location & power demands
        from specified CSV file.
        
        Parameters
        ----------
        filename : str
            CSV file containing node locations, power demands and
            source location.
        network_voltage : float
            Operating voltage of network.
        pole_cost : float
            Cost of single electrical pole.
        pole_spacing : float
            Spacing between poles in meters.
        res_per_km : float
            Cable's resistance per kilometer (ohm/km).
        max_current : float
            Cable's maximum current rating.
        cost_per_km : float
            Cable's cost per km.
        scl : float, optional
            Scales coordinates of source and nodes by chosen amount.
            The default is 1.
        max_V_drop : flaot, optional
            Maximum voltage drop. If not specified value dictated by
            voltage regulation. The default is None.
        node_ids : array-like, optional
            Array containing node identifiers. The default is None.
        V_reg : float, optional
            Maximum voltage drop as percentage of network voltage.
            The default is 6.

        Returns
        -------
        NetworkDesigner
            Returns NetworkDesigner object with specified parameters
            and data extracted from CSV file.

        """
        
        # read CSV file
        df = pd.read_csv(str(filename))
        df = df.set_index("ID")
        
        # create source and node objects from entries in CSV
        node_locs = []
        power_demands = []
        node_ids = []
        source = True
        for node_id,data in df.iteritems():
            # first entry is source
            if source:
                src_loc = (scl * int(data[0]), scl * int(data[1]))
                source = False
            
                #TODO for debug - can remove
                print(" source location")
                print(src_loc,"\n")
            
            # rest are nodes
            else:
                location = (scl * int(data[0]), scl * int(data[1]))
                node_locs.append(location)
                node_ids.append(node_id)
                power_demands.append(data[2:].tolist())

                #TODO for debug - can remove
                print(" node location")
                print(location)
                print(" node_id")
                print(node_id)
                print(" node Pdem")
                print(data[2:].tolist(),"\n")
        
        return cls(src_loc, node_locs, power_demands, network_voltage,
                   pole_cost, pole_spacing,
                   res_per_km, max_current, cost_per_km, node_ids)
    
    #-------HIGH LEVEL METHODS------------------------------------------------#
    
    def build_network(self):
        """
        Builds network using Esau-Williams CMST.

        """
        
        self._setup()
        
        self._cmst()
        
        self._disconnect_failed()
        
        self._calc_cost()
        
        self._calc_total_Pdem()
    
    def draw_graph(self, save=False):
        """
        Draws network graph.

        Parameters
        ----------
        save : bool, optional
            If True graph image is saved. The default is False.

        """
        
        x = [node.loc[0] for node in self.nodes]
        y = [node.loc[1] for node in self.nodes]
        
        # plt.figure(figsize=(10,10))
        plt.figure()
        plt.scatter(x[0],y[0],c="orange")  # source
        plt.scatter(x[1:],y[1:])  # nodes
        for i in range(len(x)):
            if i == 0:
                # plt.annotate("SRC", (x[i], y[i]))
                plt.text(x[i],y[i],"SRC",fontsize="small")
            else:
                # plt.annotate(str(i), (x[i], y[i]))
                plt.text(x[i],y[i],str(i),fontsize="small")
        plt.show
        
        if save == True:
            plt.savefig("initial layout", dpi=300)
        
        # plt.figure(figsize=(20,20))
        plt.figure()
        G = nx.Graph()

        # filter valid edges (value not 0 in final connection matrix)
        edges_valid = np.transpose(self.final_connect.nonzero())
        # filter invalid edges
        invalid_connect = self.connections - self.final_connect
        edges_invalid = np.transpose(invalid_connect.nonzero())
        pos = dict()
        for node_idx,node in enumerate(self.nodes):
            pos[node_idx] = node.loc
        
        G.add_edges_from(edges_valid)
        G.add_edges_from(edges_invalid)
        
        color_map = []
        for node_idx in G:
            node = self.nodes[node_idx]
            if type(node) == Source:
                color_map.append("tab:orange")
            elif node.csrt_sat:
                color_map.append("tab:blue")
            else:
                color_map.append("tab:red")
                
        nx.draw_networkx_nodes(G, node_color=color_map, pos=pos)
        nx.draw_networkx_edges(G, pos=pos, edgelist=edges_valid)
        nx.draw_networkx_labels(G, pos=pos)
        plt.show()
        
        if save == True:
            plt.savefig("final network", dpi=300)
    
    def _setup(self):
        """
        Initialisation phase for CMST.

        """

        # all nodes part of own subtree initially
        self._init_subtrees()
        
        # create & populate connection/distance/checked path matrices
        self._init_matrices()
        
        # calculate resistance of line between nodes and source
        # and test voltage constraints
        self._init_constraints()
        
        print("\nSETUP DONE!")
    
    def _cmst(self):
        """
        Runs CMST algorithm to create network.

        """
        
        further_improvements = True
        self.old_best_gate = None
        self.old_best_node = None
        
        loop = 0
        
        while further_improvements == True: #and loop < 4:
            
            loop += 1
            print("-------------------------------")
            print("\nloop " + str(loop))
            
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
    
    def _calc_cost(self):
        """
        Calculates the network's total cost and total cable length.

        """
        
        self.total_length = np.sum(self.connections) / 2
        self.line_cost = self.total_length * self.cost_meter
        self.num_poles = math.ceil(self.total_length / self.pole_spacing)
        self.num_poles += len(self.nodes)
        self.poles_cost = self.num_poles * self.pole_cost
        
        self.total_cost = self.line_cost + self.poles_cost
        
        # print("\ntotal length: " + str(round(self.total_length,2)) + " m")
        # print("\ntotal cost: £" + str(round(self.total_cost,2)))
    
    def _calc_total_Pdem(self):
        """
        Calculates network's total power demand.
        Does not include any losses.

        """
        
        # sum all of power demands
        net_Pdem = sum([node.Pdem for node in self.nodes 
                        if type(node) == Node and node.csrt_sat])
        
        # create yearly power demand profile
        net_Pdem = np.tile(net_Pdem, 365)
        self.total_Pdem = net_Pdem
    
    #-------INITIALISATION PHASE----------------------------------------------#
    
    def _init_subtrees(self):
        """
        Sets the subtree of each node to iteself. Only used in initialisation
        phase for Esau-Williams algorithm.

        """
        
        for idx, node in enumerate(self.nodes):
            if type(node) == Source:
                continue
            else:
                node.subtree = idx
    
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

        for node_idx, node in enumerate(self.nodes):
            
            if type(node) == Node:
                
                # calculate resistance between each node and parent (SRC)
                self.calculate_res(node)
                
                # calculate current drawn by node    I(t) = Pdem(t) / Vnet [DC]
                node.I = node.Pdem / self.Vnet

                # voltage drops is current * line resistance
                voltage_drops = node.line_res * node.I
                
                if np.max(voltage_drops) > self.Vdrop_max:
                    node.csrt_sat = False
                else:
                    node.csrt_sat = True
                
                # update path between node and parent (SRC) as checked
                self.path_checked[node_idx,node.parent] = True
                self.path_checked[node.parent,node_idx] = True
                
            else:
                pass
    
    #-------CMST METHODS------------------------------------------------------#
    
    def _candidate_nodes(self):
        """
        Finds two candidate nodes for new connection. Candidate nodes
        are (1) best node to connect to, (2) best gate to connect.

        Returns
        -------
        Node
            Best gate to connect.
        Node
            Best node to connect to.

        """
        
        best_tradeoff = 0
        best_gate_idx = None
        best_node_idx = None
        
        for gate_idx, gate in enumerate(self.nodes):
            
            if type(gate) == Source:
                continue
            
            if gate.isgate() == False:
                continue
            
            # gate_idx = self.nodes.index(gate)
            else:
                min_distance = self.distances[gate_idx,0]  # distance gate-SRC
            
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
            
            if tradeoff > 0 and tradeoff > best_tradeoff:
                best_tradeoff = tradeoff
                best_gate_idx = temp_best_gate_idx
                best_node_idx = temp_best_node_idx
        
        if best_gate_idx == None or best_node_idx == None:  # no new candidates
            return False, False
        else:
            return best_gate_idx, best_node_idx  # new candidates found
    
    def _save_state(self):
        """
        Saves the network's current state.

        """
        
        self.prev_nodes = copy.deepcopy(self.nodes)
        self.prev_connections = copy.deepcopy(self.connections)
        
    def _load_prev_state(self):
        """
        Restores nodes and connections from last saved state.

        """
        
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
        
        # disconnect gate from source in adj matrix
        self.connections[gate_idx,0] = 0
        self.connections[0,gate_idx] = 0
        
        # update subtree for all nodes in gate subtree
        for subnode in self.nodes:
            if type(subnode) == Source:
                continue
            elif subnode == node or subnode == gate:
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
        """
        Resets check variables of each node in network.

        """
        
        for node in self.nodes:
            if type(node) == Node:
                node.I_checked = False
                node.V_checked = False
                
                node.I_line = np.zeros(len(node.Pdem))
    
    def _test_current(self,gate_idx):
        """
        Tests currents of all nodes in subtree, starting from gate
        node that has just been connected.

        Parameters
        ----------
        gate_idx : int
            Index of gate node that has been connected to new subtree.

        Returns
        -------
        bool
            True if all currents valid. False if any current invalid.

        """
        
        active_idx = gate_idx
        active_node = self.nodes[gate_idx]
        
        constraint_broken = False
        
        while type(active_node) != Source and constraint_broken == False:
            
            print(active_idx)
            
            all_checked = False
            
            # if active node has children
            if active_node.has_children() == True:
                
                # search for child with unchecked current
                for child_idx in active_node.children:
                    child = self.nodes[child_idx]
                    
                    # child with unchecked current found
                    # becomes active and stops searching
                    if child.I_checked == False:
                        active_idx = child_idx
                        active_node = child
                        break
                    
                    # all children checked
                    elif child_idx == active_node.children[-1]:
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
                if (np.max(active_node.I_line) > self.Imax):
                    constraint_broken = True
                    
                    print("failed current check")
                
                # mark node as checked
                active_node.I_checked = True
                
                # move upstream --> parent node becomes active node
                active_idx = active_node.parent
                active_node = self.nodes[active_idx]
        
        if constraint_broken:
            return False
        else:
            return True
    
    def _test_voltage(self,gate_idx):
        """
        Tests voltages of all nodes in subtree in which new connection
        has been made.

        Parameters
        ----------
        gate_idx : int
            Index of gate node that has been connected to new subtree.

        Returns
        -------
        bool
            True if all voltages valid. False if any voltage invalid.

        """
        
        active_idx = self.nodes[gate_idx].subtree
        active_node = self.nodes[active_idx]
        
        constraint_broken = False
        
        while type(active_node) != Source and constraint_broken == False:
            
            print(active_idx)
            
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
                    
                    print("voltage check failed")
            
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
            return True
    
    def _test_constraints(self,gate_idx):
        """
        Tests constraints on newly connected subtree.
        Updates constraint attribute in nodes.

        Parameters
        ----------
        gate_idx : int
            Index of gate node that has been connected to new subtree..

        Returns
        -------
        bool
            True if constraints satisfied. False if constraints broken.

        """
        
        self._reset_checks()
        
        print("testing current")
        I_test = self._test_current(gate_idx)
    
        print("testing voltage")
        V_test = self._test_voltage(gate_idx)
        
        gate_node = self.nodes[gate_idx]
        
        if I_test == False or V_test == False:
            gate_node.csrt_sat = False
            return False
        else:
            gate_node.csrt_sat = True
            return True
        
    def _disconnect_failed(self):
        """
        Undoes invalid connections if constraints not satisfied.

        """
        
        self.final_connect = self.connections.copy()
        
        for node_idx, node in enumerate(self.nodes):
            if type(node) != Source and node.csrt_sat == False:
                self.final_connect[node_idx,:] = 0
                self.final_connect[:,node_idx] = 0
