# -*- coding: utf-8 -*-
"""
Created on Fri Sep  5 21:39:46 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Custom classes
from components.circuit_component import CircuitComponent
from enums.component_type import ComponentType
from enums.calculation_mode import CalculationMode
from enums.switch_condition import SwitchCondition

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class Switch(CircuitComponent):
    def __init__(self, component_data):
        
        # Inherit superclass prop
        super().__init__(component_data)
        
        # Enforce type setting
        self.component.ctype = ComponentType.SWITCH
        
    def update(self, time=None):
        
        # Update switch status
        self.resistance()
        
        if self.component.mode == CalculationMode.VOLTAGE:
            self.voltage()
            
        elif self.component.mode == CalculationMode.CURRENT:
            self.current()
                
        else:    
            raise ValueError('Error: Specify calculation mode for Switch '+
                             self.component.name)
    def stamp(self, A, b, n1, n2, voltage_source_index=None, i_guess=None):
        # Used for matrix formulation in network class
        
        # # Get component node indices
        # n1 = node_map[self.component.node1]
        # n2 = node_map[self.component.node2]
        
        if (self.component.resistance is not None and
            self.component.resistance > 0):

            # Calculate conductance
            G = 1.0 / self.component.resistance
            
            # Update A array, assumes A / b passed as references
            A[n1, n1] += G
            A[n2, n2] += G
            A[n1, n2] -= G
            A[n2, n1] -= G
        
        else:
            raise ValueError("Switch has None or Negative resistance")

    def resistance(self):
        # Calculate resistance based on switch condition
        if self.component.scond == SwitchCondition.OPEN:
            self.component.resistance = 1e10
        elif self.component.scond == SwitchCondition.CLOSED:
            self.component.resistance = 1e-10
        else:
            raise ValueError(
                f'Error: Switch {self.component.name} has invalid switch mode')

    def voltage(self):
        # Calculate voltage across resistor
        self.component.voltage = (self.component.current * 
                                  self.component.resistance)
        
    def current(self):
        # Calculate current across resistor
        if self.component.resistance <= 0:
            raise ValueError(
                f'Error: Resistor {self.component.name} has invalid '
                f'resistance: {self.component.resistance}'
                )
        
        self.component.current = (self.component.voltage / 
                                  self.component.resistance)
        
