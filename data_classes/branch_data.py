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
from enums.component_type import ComponentType

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

@dataclass
class BranchData:
    name: str = 'Default'
    node1: str = 'default_n1'
    node2: str = 'default_n2'
    node1_voltage: float = 0.0
    node2_voltage: float = 0.0
    voltage_drop: float = 0.0
    current: float = 0.0
    resistance: float = 0.0
    ctype: ComponentType = ComponentType.RESISTOR
