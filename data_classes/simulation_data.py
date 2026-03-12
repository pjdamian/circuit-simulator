# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 22:10:52 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in classes
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

@dataclass
class SimulationData:
    name: str = 'sim1'
    time: np.ndarray = field(default_factory=lambda: np.array([0],dtype=float))
    
    # Network information
    node_names: List[str] = field(default_factory=list)
    branch_names: List[str] = field(default_factory=list)
    node_x: Optional[np.ndarray] = None
    node_y: Optional[np.ndarray] = None
    
    # Results
    node_v: Optional[np.ndarray] = None
    branch_v: Optional[np.ndarray] = None
    branch_i: Optional[np.ndarray] = None