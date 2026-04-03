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
from scipy.sparse import lil_matrix, issparse
from scipy.sparse.linalg import spsolve

# Custom modules
from enums.component_type import ComponentType
from enums.discretization_type import DiscretizationType
from data_classes.node_data import NodeData
from data_classes.branch_data import BranchData
from data_classes.simulation_data import SimulationData
from config_classes.numeric_checks import MathChecks
from networks.input_driver import InputDriver
from data_classes.stamp_context import StampContext

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class Network:
    def __init__(self, 
                 node_reporting=False, 
                 branch_reporting=False,
                 numerics: MathChecks | None = None,
                 discretization=DiscretizationType.BACKWARD_EULER,
                 verbose=False):
        
        # Setting arguments
        self.node_reporting = node_reporting
        self.branch_reporting = branch_reporting
        self.numerics = numerics or MathChecks()
        self.discretization = discretization
        self.verbose = verbose
        
        # Initializing attributes        
        self.graph = nx.MultiGraph() # nx.Graph() # Parallel Edges 
        self.mode = None
        self.ground_node = None
        self.node_indices = {} # name -> index node mapping
        self.node_list = [] # ordered list of nodes
        self.node_voltages = {}
        self.v_source_list = []
        self.num_nodes = 0
        self.num_v_sources = 0
        self.node_report = None
        self.branch_report = None
        
        # Discretization check - allows swapping between discretization schemes
        # first dt vs rest or after special spikes in data
        self.default_dt = True
        
    def add_node(self, name, pos=None):
        self.graph.add_node(name)
        if pos:
            self.graph.nodes[name]['pos'] = pos
            
    def add_component(self, n1, n2, component):
        
        # Overwrite node names with provided nodes
        component.component.node1 = n1
        component.component.node2 = n2
        
        # Add component as an edge
        self.graph.add_edge(n1, n2, key=component.component.name, 
                            component=component)
        
    def solve(self, 
              time: np.ndarray | None = None,
              input_driver: InputDriver | None = None):
        
        # Prune isolated nodes, Build node list
        self._local_print('\nPruning isolated nodes')
        self._prune_isolated_nodes()
        
        # Build lists, lookups, and dictionaries
        self._local_print('\nBuilding lists, lookups, and dictionaries')
        self._build_node_list()        
        self._build_voltage_list()
        self._build_branch_list()
        self._build_component_lookup()
        
        # Initialize output storage, sim_data
        self._get_simulation_length(time)
        sim_data = self._init_storage(time)
        
        # Evaluate single timestep
        if self.num_steps == 1:
            self._timestep(dt=None)
            self._write_step(sim_data, 0)
            
        else:

            # Error for missing input_driver 
            if input_driver is None:
                raise ValueError("Transient behavior needs input_driver object")

            # calculate dts, initialize default dt
            dt_vec = np.diff(time)
            
            # vectorized dt check
            self._guard_dt_min_vec(dt_vec)
            
            # Loop over all dts - first time step will be the network solved 
            # for the given component conditions
            for k, dt in enumerate(dt_vec, start=0):
                
                # Get new time stamp
                t_new = float(sim_data.time[k])
                
                # Apply inputs
                input_driver.apply(self, t=t_new, k=k)
                
                # Evaluate and store timestep
                self._timestep(dt=dt)
                self._write_step(sim_data, k)
                
                # Update default_dt
                if self.default_dt:
                    self.default_dt = False
                
        # Store sim_data on object
        self.sim_data = sim_data
            
    def _build_branch_list(self):
        
        self.branch_list = [(n1, n2, d["component"]) for n1, n2, d in 
                            self.graph.edges(data=True)]
        
    def _build_component_lookup(self):
        
        self.components_by_name = {}
        
        for _, _, data in self.graph.edges(data=True):
            
            c_obj = data["component"]
            name = c_obj.component.name
            
            if ((name in self.components_by_name) and 
                ((c_obj.component.ctype is ComponentType.VOLTAGE_SOURCE) or 
                (c_obj.component.ctype is ComponentType.CURRENT_SOURCE))):
                raise ValueError(f"Duplicate component name: {name}")
                
            self.components_by_name[name] = c_obj
        
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
            
        self.num_nodes = len(self.node_indices)

    def _build_voltage_list(self):
        
        v_source_list = []
        for _,_, data in self.graph.edges(data=True):
            
            c = data['component'].component
            
            n1 = c.node1
            n2 = c.node2
            
            if c.ctype == ComponentType.VOLTAGE_SOURCE:
                v_source_list.append((n1, n2, data['component']))
                
        self.v_source_list = v_source_list
        self.num_v_sources = len(v_source_list)

    def _check_matrix(self, A):
        
        if self.verbose:
            self._local_print('Checking A matrix for numerical stability')
        
            # Get rank of matrix
            
            # Check for sparse matrices
            if hasattr(A, 'toarray'):
                A = A.toarray()
                
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
                self._local_print("row norms:", [f"{i}:{row_norms[i]:.2e}" for 
                                                 i in range(A.shape[0])])
                
                # map rows to meaning
                rev_nodes = {idx:name for name, idx in 
                             self.node_indices.items()}
                
                for i in range(A.shape[0]):
                    if row_norms[i] < 1e-12:
                        if i < n:
                            label = f"Node {rev_nodes[i]}"
                        elif i < n + m:
                            k = i-n
                            label = f"Voltage Source {self.v_source_list[k]}"
                        self._local_print(f"Row {i}: {label}")
                        
                raise ValueError("A in Ax=b is rank deficient")
    
    def _create_Ab(self, dt):
        
        numel = self.num_nodes + self.num_v_sources
        
        # Switching to sparse matrix solve
        if numel < self.numerics.sparse_threshold:
            A = np.zeros((numel, numel), dtype=float)
        else:
            A = lil_matrix((numel, numel))
        
        b = np.zeros((numel,), dtype=float)
        
        ctx = StampContext(
            dt=dt,
            default_dt= self.default_dt,
            discretization= self.discretization)
        
        # Stamp A matrix for passive components
        for _,_, data in self.graph.edges(data=True):
            
            c_obj = data['component']
            
            n1 = c_obj.component.node1
            n2 = c_obj.component.node2
            
            if c_obj.component.ctype != ComponentType.VOLTAGE_SOURCE:
                c_obj.stamp(A, 
                            b, 
                            self.node_indices[n1], 
                            self.node_indices[n2], 
                            ctx)
        
        # Stamp A matrix for voltage sources
        for k, (n1, n2, vs) in enumerate(self.v_source_list):
            
            # n1, n2 are directed nodes (self._voltage_list() populates via 
            # assumed orientation)
            
            # Calculate voltage source index
            vs_ctx = StampContext(voltage_source_index=self.num_nodes+k)
            
            vs.stamp(A, b,self.node_indices[n1], self.node_indices[n2], vs_ctx)
            
        return A, b

    def _get_branch_data_list(self):
        
        branch_data_list = []
        for _,_, data in self.graph.edges(data=True):
            
            c = data["component"].component
            
            n1 = c.node1
            n2 = c.node2
            
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

    def _get_node_data_list(self):
        # get net currents
        node_i = {node: 0.0 for node in self.graph.nodes}
        
        for _,_, data in self.graph.edges(data=True):
            
            c = data['component'].component
            
            n1 = c.node1
            n2 = c.node2
            
            i = getattr(c, "current", 0.0)
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
    
    def _get_simulation_length(self, time: np.ndarray):
        
        if time is not None:
            self.num_steps = max(1,len(time))
        else:
            self.num_steps = 1

    def _guard_dt(self, dt):
                
        if dt is None:        
            # Raise error if there are any capacitors
            if any(d['component'].component.ctype == ComponentType.CAPACITOR 
                   for _,_,d in self.graph.edges(data=True)):
                raise ValueError("Unsupported: Capacitor(s) with single DT.")
            
            # Raise error if there are any capacitors
            if any(d['component'].component.ctype == ComponentType.INDUCTOR 
                   for _,_,d in self.graph.edges(data=True)):
                raise ValueError("Unsupported: Inductor(s) with single DT.")
        
        elif dt < self.numerics.min_dt:
            raise ValueError(f"DT must be greater than {self.numerics.min_dt}")
    
    def _guard_dt_min_vec(self, dt_vec):
            
        dt_check = dt_vec < self.numerics.min_dt
        if any(dt_check):
            raise ValueError(
                f"DT must be larger than min DT: {self.numerics.min_dt}")
    

        
    def _init_storage(self, time: np.ndarray):
        
        if self.num_steps > 1:
            steps = self.num_steps - 1
            local_time = time[1:]
        else:
            steps = 1
            local_time = np.array([0],dtype=float)
        
        sim_data = SimulationData(time=local_time)
        sim_data.node_names = list(self.node_list)
        sim_data.branch_names = [c.component.name for _, _, c in 
                                 self.branch_list]        
        sim_data.node_v = np.zeros((steps, self.num_nodes), 
                                   dtype=float)
        sim_data.branch_v = np.zeros((steps, len(self.branch_list)), 
                                     dtype=float)
        sim_data.branch_i = np.zeros((steps, len(self.branch_list)), 
                                     dtype=float)
        
        return sim_data
    
    def _local_print(self, *args):
        
        if self.verbose:
            print(*args)
            
    def _prune_isolated_nodes(self):
        
        # get isolated nodes
        iso_nodes = list(nx.isolates(self.graph))
        
        if iso_nodes:
            self._local_print(f"\tWARNING - dropping isolated nodes: {iso_nodes}")
            self.graph.remove_nodes_from(iso_nodes)
    
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
    
    def _solve(self, A, b):
        
        if issparse(A):
            A = A.tocsr()
            x = spsolve(A, b)
        else:
            x = np.linalg.solve(A, b)
        
        return x
    
    def _store_data(self, x, dt):
        
        # Store node voltages
        for node, idx in self.node_indices.items():
            self.node_voltages[node] = x[idx]
        
        # Stamp Context
        ctx = StampContext(dt=dt, 
                           default_dt=self.default_dt,
                           discretization=self.discretization)
        
        # Store voltage source currents 
        for k, (_, _, vs) in enumerate(self.v_source_list):
            
            # Calculate voltage source index
            vs_idx = self.num_nodes + k
            
            # Update voltage source current
            vs.post_solve(x[vs_idx], ctx)
            
        # Store voltage drops, currents for all components
        for _, _, data in self.graph.edges(data=True):
            
            c_obj = data['component']
            
            # skip voltage sources
            if c_obj.source:
                pass
            else:
                # Extract node specific orientation
                n1 = c_obj.component.node1
                n2 = c_obj.component.node2
                
                # Store voltage drop across component
                voltage_new = self.node_voltages[n1] - self.node_voltages[n2]
                
                c_obj.post_solve(voltage_new, ctx)
                
    def _timestep(self, dt=None):
        
        self._guard_dt(dt)
            
        self._local_print('\nSolving circuit using Modified Nodal Analysis')
        
        # Update component state
        self._update_comps()

        # Generate A, b matrices
        self._local_print('Generating A matrix, b vector')
        A, b = self._create_Ab(dt)
        
        # Set ground
        self._local_print('Setting ground node')
        gnd_idx = self.node_indices[self.ground_node]
        
        A[gnd_idx, :] = 0.0
        A[:, gnd_idx] = 0.0
        
        A[gnd_idx, gnd_idx] = 1.0
        b[gnd_idx] = 0.0


        # Check for matrix issues
        self._check_matrix(A)
        
        # Solve Ax = b
        self._local_print('Solving Ax=b')
        x = self._solve(A, b)
        
        # Store solved data to objects in graph / network
        self._local_print('Storing network data')
        self._store_data(x, dt)
        
        # Generate final node list
        if self.node_reporting:
            self.node_report = self._get_node_data_list()
            self._local_print('\nReporting Node Data\n')
            self._local_print(self.node_report)

        if self.branch_reporting:
            self.branch_report = self._get_branch_data_list()
            self._local_print('\nReporting Branch Data\n')
            self._local_print(self.branch_report)

    def _update_comps(self):
        
        for _, _, data in self.graph.edges(data=True):
                data['component'].update()
        
    def _write_step(self, sim_data: SimulationData, step: int):
        # nodes
        for j, node in enumerate(self.node_list):
            sim_data.node_v[step, j] = float(self.node_voltages[node])
            
        for k, (_, _, c) in enumerate(self.branch_list):
            sim_data.branch_v[step, k] = float(c.component.voltage)
            sim_data.branch_i[step, k] = float(c.component.current)
        