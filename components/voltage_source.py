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

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class VoltageSource(CircuitComponent):
    def __init__(self, component_data):
        
        # Inherit superclass prop
        super().__init__(component_data)
        
        # Enforce type setting
        self.component.ctype = ComponentType.VOLTAGE_SOURCE
        
    def update(self, time=None):
        
        if self.component.mode == CalculationMode.VOLTAGE:
            self.voltage()
            
        elif self.component.mode == CalculationMode.CURRENT:
            self.current()
        
        elif self.component.mode == CalculationMode.RESISTANCE:
            self.resistance()
        
        else:    
            raise ValueError('Error: Specify calculation mode for Voltage '+
                             self.component.name)
    
    def stamp(self, A, b, n1, n2, voltage_source_index, i_guess=None):
        # Used for matrix formulation in network class
        
        # Check for ideal parameters        
        if self.component.ideal_params is not None:
            r_int = self.component.ideal_params.int_resistance
            v_rise = self.component.ideal_params.ideal_voltage
        else:
            raise ValueError('Error: Specify voltage source ideal parameters')
        
        # Update A matrix with voltage source component
        A[n1, voltage_source_index] += 1.0
        A[voltage_source_index, n1] += 1.0
        A[n2, voltage_source_index] -= 1.0
        A[voltage_source_index, n2] -= 1.0
        

        if r_int > 0:
            A[voltage_source_index,voltage_source_index] -= r_int
                    
        # Update voltage in b
        # negative voltage -> voltage sources introduce a rise between 
        # inlet node n1, and outlet node n2. 
        b[voltage_source_index] -= v_rise
    
    def voltage(self):
        # Calculate voltage across source
        self.component.voltage = (self.component.ideal_params.ideal_voltage - 
                                 self.component.current * 
                                 self.component.ideal_params.int_resistance)
        
    def current(self):
        # Calculate current across voltage source
        if self.component.ideal_params.int_resistance <= 0:
            raise ValueError(
                f'Error: Voltage source {self.component.name} has invalid '
                f'resistance: {self.component.ideal_params.int_resistance}'
                )
        
        self.component.current = ((self.component.ideal_params.ideal_voltage - 
                                  self.component.voltage) / 
                                  self.component.ideal_params.int_resistance)
        
    def resistance(self):
        # Calculate resistance
        if self.component.current == 0:
            raise ValueError(
                f'Error: Voltage source {self.component.name} has invalid '
                f'current: {self.component.current}'
                )
            
        self.component.ideal_params.int_resistance = (
            (self.component.ideal_params.ideal_voltage - 
            self.component.voltage)/abs(self.component.current)
            )
        
        # Store internal resistance as voltage source resistance
        self.component.resistance = self.component.ideal_params.int_resistance
        