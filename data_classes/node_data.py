# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 22:10:52 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in classes
from dataclasses import dataclass

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

@dataclass
class NodeData:
    name: str = 'Default'
    voltage: float = 0.0
    net_current: float = 0.0
    pos: tuple[float, float] = (0.0, 0.0)