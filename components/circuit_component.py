# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 21:42:02 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Custom classes
from data_classes.component_data import ComponentData


# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class CircuitComponent:
    def __init__(self, component_data: ComponentData):
        # self.name = name
        # self.ctype = ctype
        self.component = component_data
    
    def update(self):
        # Purpose: update component internal properties
        # Overwrite with subclass implementation
        raise NotImplementedError('Components must implement this method')
    
    def stamp(self):
        # Purpose: populate A, b from Ax = b formulation in networks class
        # Overwrite with subclass implementation
        raise NotImplementedError('Components must implement this method')