# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 21:42:02 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

from abc import ABC, abstractmethod

# Custom classes
from data_classes.component_data import ComponentData
from data_classes.stamp_context import StampContext
# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class CircuitComponent(ABC):
    def __init__(self, component_data: ComponentData):
        self.component = component_data
        self.source = False
    
    def _store_lpv(self):
        # Store lpv for circuit component discretization (ie inductors, 
        # capacitors)
        if self.component.discrete_data is not None:
            d = self.component.discrete_data
            
            d.lpv2_voltage = d.lpv1_voltage
            d.lpv1_voltage = self.component.voltage
            d.lpv2_current = d.lpv1_current
            d.lpv1_current = self.component.current
    
    # @abstractmethod forces an error at subclass creation instead of runtime 
    # for improperly created components
    @abstractmethod
    def update(self):
        # Purpose: update component internal properties
        # Overwrite with subclass implementation
        raise NotImplementedError('Components must implement this method')
    
    @abstractmethod
    def stamp(self, A, b, n1, n2, ctx: StampContext):
        # Purpose: populate A, b from Ax = b formulation in networks class
        # Overwrite with subclass implementation
        raise NotImplementedError('Components must implement this method')
        
    @abstractmethod
    def post_solve(self, solution_variable: float, ctx: StampContext):
        # Purpose: update component properties with solution vector info
        # Overrite with subclass implementation
        raise NotImplementedError('Components must implement this method')