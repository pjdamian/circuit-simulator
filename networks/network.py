# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 21:11:15 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built-in
import networkx as nx
import numpy as np

# Custom modules
from enums.component_type import ComponentType
from data_classes.node_data import NodeData
from data_classes.branch_data import BranchData

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class Network:
    def __init__(self, node_reporting=False, branch_reporting=False):
        self.graph = nx.Graph()
        self.mode = None
        self.ground_node = None
        self.node_indices = {} # name -> index node mapping
        self.node_list = [] # ordered list of nodes
        self.node_voltages = {}
        
        self.node_reporting = node_reporting
        self.node_report = None
        
        self.branch_reporting = branch_reporting
        self.branch_report = None
        
    def add_node(self, name, pos=None):
        self.graph.add_node(name)
        if pos:
            self.graph.nodes[name]['pos'] = pos
            
    def add_component(self, n1, n2, component):
        self.graph.add_edge(n1, n2, component=component)
        
    def _set_mode(self, mode):
        self.mode = mode
        for _, _, data in self.graph.edges(data=True):
            data['component'].component.mode=mode
    
    def _set_ground(self):
        
        if self.ground_node is None:
            
            nodes = list(self.graph.nodes)
            
            if 'n0' in nodes:
                self.ground_node = 'n0'
            elif 'gnd' in nodes:
                self.ground_node = 'gnd'
            else:
                self.ground_node = nodes[0]
    
    def _build_node_list(self):
        
        self._set_ground()
        
        # Clear node indices and lists
        self.node_indices = {}
        self.node_list = []
        
        # Set index
        idx=0
        
        for node in self.graph.nodes:
            self.node_indices[node] = idx
            self.node_list.append(node)
            idx += 1
            
        return len(self.node_indices)

    def _prune_isolated_nodes(self):
        
        # get isolated nodes
        iso_nodes = list(nx.isolates(self.graph))
        
        if iso_nodes:
            print(f"\tWARNING - dropping isolated nodes: {iso_nodes}")
            self.graph.remove_nodes_from(iso_nodes)
    
    def _check_matrix(self, A, v_source_list):
        
        # Get rank of matrix
        rank = np.linalg.matrix_rank(A)
        
        if rank < A.shape[0]:
            
            # Node-voltage unknowns
            n = len(self.node_indices)
            
            # Number of voltage sources
            m = sum(1 for _,_,d in self.graph.edges(data=True)
                    if (d['component'].component.ctype == 
                        ComponentType.VOLTAGE_SOURCE))
            
            # row information
            row_norms = np.linalg.norm(A, axis=1)
            print("row norms:", [f"{i}:{row_norms[i]:.2e}" for i in 
                                 range(A.shape[0])])
            
            # map rows to meaning
            rev_nodes = {idx:name for name, idx in self.node_indices.items()}
            
            for i in range(A.shape[0]):
                if row_norms[i] < 1e-12:
                    if i < n:
                        label = f"Node {rev_nodes[i]}"
                    elif i < n + m:
                        k = i-n
                        label = f"Voltage Source {v_source_list[k]}"
                    print(f"Row {i}: {label}")
                    
            raise ValueError("A in Ax=b is rank deficient")
    
    def _get_node_data_list(self):
        # get net currents
        node_i = {node: 0.0 for node in self.graph.nodes}
        for n1, n2, data in self.graph.edges(data=True):
            comp = data['component'].component
            i = getattr(comp, "current", 0.0)
            node_i[n1] -= i
            node_i[n2] += i
            
        node_data_list = []
        for node in self.graph.nodes:
            node_data_list.append(NodeData(name=node,
                                           voltage=
                                           self.node_voltages.get(node,0.0),
                                           net_current=node_i[node],
                                           pos=
                                           self.graph.nodes[node].get("pos")))
            
        return node_data_list
    
    def _get_branch_data_list(self):
        
        branch_data_list = []
        for n1, n2, data in self.graph.edges(data=True):
            c = data["component"].component
            
            branch_data_list.append(
                BranchData(
                    name=c.name,
                    node1=n1,
                    node2=n2,
                    node1_voltage=self.node_voltages.get(n1, 0.0),
                    node2_voltage=self.node_voltages.get(n2, 0.0),
                    voltage_drop=c.voltage,
                    current=getattr(c,'current',0.0),
                    resistance=getattr(c,'resistance',None),
                    ctype=c.ctype.value))
            
        return branch_data_list
    
    def solve(self, time=None):
        
        print('\nSolving circuit using Modified Nodal Analysis')
        
        # Update component state
        for _, _, data in self.graph.edges(data=True):
            # component=data['component']
            if time is not None:
                data['component'].update(time)
            else:
                data['component'].update()
                
        # Build node list
        print('\n1: Pruning isolated nodes')
        self._prune_isolated_nodes()
        num_nodes = self._build_node_list()        
        
        # Treat voltage sources
        v_source_list = []
        for n1, n2, data in self.graph.edges(data=True):
            c = data['component'].component
            if c.ctype == ComponentType.VOLTAGE_SOURCE:
                v_source_list.append((n1, n2, data['component']))
        
        num_v_sources = len(v_source_list)
        
        # Generate A, b matrices
        print('2: Generating A matrix, b vector')
        numel = num_nodes + num_v_sources
        
        A = np.zeros((numel, numel), dtype=float)
        b = np.zeros((numel,), dtype=float)
        
        # Stamp A matrix for passive components
        for n1, n2, data in self.graph.edges(data=True):
            
            c_obj = data['component']
            
            # Passive components only
            if c_obj.component.ctype in (ComponentType.RESISTOR, 
                                         ComponentType.SWITCH):
                c_obj.stamp(A=A,
                            b=b,
                            n1=self.node_indices[n1],
                            n2=self.node_indices[n2],
                            voltage_source_index=None)
                    
        # Stamp A matrix for voltage sources
        for k, (n1, n2, vs) in enumerate(v_source_list):
            
            # Calculate voltage source index
            vs_idx = num_nodes+k
            
            vs.stamp(A=A,
                     b=b,
                     n1=self.node_indices[n1],
                     n2=self.node_indices[n2],
                     voltage_source_index=vs_idx)

        # Set ground
        print('3: Setting ground node')
        gnd_idx = self.node_indices[self.ground_node]
        
        A[gnd_idx, :] = 0.0
        A[:, gnd_idx] = 0.0
        
        A[gnd_idx, gnd_idx] = 1.0
        b[gnd_idx] = 0.0


        # Check for matrix issues
        print('4: Checking A matrix for numerical stability issues')
        self._check_matrix(A, v_source_list)
        
        # Solve Ax = b
        print('5: Solving Ax=b')
        x = np.linalg.solve(A, b)
        
        # Store node voltages
        for node, idx in self.node_indices.items():
            self.node_voltages[node] = x[idx]
            
        # Store voltage source currents 
        for k, (n1, n2, vs) in enumerate(v_source_list):
            
            # Calculate voltage source index
            vs_idx = num_nodes + k
            
            # update current
            vs.component.current = x[vs_idx]
            
        # Store voltage drops, currents for all components
        for n1, n2, data in self.graph.edges(data=True):
            
            c_data = data['component'].component
            
            # Store voltage drop across component
            c_data.voltage = self.node_voltages[n1] - self.node_voltages[n2]
            
            # Propagate currents
            if c_data.ctype in (ComponentType.RESISTOR, ComponentType.SWITCH):
                
                if (c_data.resistance is not None and c_data.resistance != 0):
                    c_data.current = c_data.voltage/c_data.resistance
                else:
                    # Short circuit when resistance = 0
                    c_data.current = np.inf
                    
        # Generate final node list
        if self.node_reporting:
            self.node_report = self._get_node_data_list()
            print('\nReporting Node Data\n')
            print(self.node_report)

        if self.branch_reporting:
            self.branch_report = self._get_branch_data_list()
            print('\nReporting Branch Data\n')
            print(self.branch_report)