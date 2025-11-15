# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 22:19:53 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in
from enum import Enum

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class ComponentType(Enum):
    RESISTOR = 'resistor'
    VOLTAGE_SOURCE = 'voltage_source'
    CURRENT_SOURCE = 'current_source'
    SWITCH = 'switch'
    NODE = 'node'