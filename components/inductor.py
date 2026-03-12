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
from enums.discretization_type import DiscretizationType

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class Inductor(CircuitComponent):
    def __init__(self, component_data):
        
        # Inherit superclass prop
        super().__init__(component_data)
        
        # Enforce type setting
        self.component.ctype = ComponentType.INDUCTOR
        
    def update(self):
        """
        update method for capacitor meant to preserve usage in network class
        """
        
        # if self.component.mode == CalculationMode.VOLTAGE:
        #     self.voltage()
            
        # elif self.component.mode == CalculationMode.CURRENT:
        #     self.current()
        
        # elif self.component.mode == CalculationMode.RESISTANCE:
        #     self.resistance()
        
        # else:    
        #     raise ValueError('Error: Specify calculation mode for Capacitor '+
        #                      self.component.name)
    
        pass
        
    def stamp(self, A, b, n1, n2, dt, voltage_source_index=None, 
              default_dt=True, 
              discretization=DiscretizationType.BACKWARD_EULER):
        """
        Objective: Update A matrix and b vector to solve the network problem

        Parameters
        ----------
        A : Float, Array
            Coefficient array characterizing the network.
        b : Float, Vector
            Source vector characterizing the network.
        n1 : Integer, Scalar
            Index for for the first node associated with this component.
        n2 : Integer, Scalar
            Index for for the second node associated with this component.
        dt : Float, Scalar
            Timestep required to c.
        dV_lpv : Float, Scalar
            Drop in voltage across the capacitor.
        voltage_source_index : Integer, Scalar, optional
            Index used for voltage source components. The default is None.
        i_guess : Float, Scalar, optional
            Guessed current for the given component. The default is None.

        Raises
        ------
        ValueError
            Capacitor has None or Negative Capacitance. Cap

        Returns
        -------
        None.

        """
        # Objective: Update A matrix and b vector to solve the network problem

        # Used for matrix formulation in network class
        
        # Get component node indices
        # n1 = node_map[self.component.node1]
        # n2 = node_map[self.component.node2]
        
        if dt is None:
            raise ValueError("Invalid dt for Inductor calculation")
        
        if (self.component.inductance is not None and
            self.component.inductance > 0):

            # Calculate stamping quantities
            if ((discretization == DiscretizationType.BACKWARD_EULER) or 
                default_dt):
                G = dt / self.component.inductance
                Ieq = self.component.discrete_data.lpv1_current
            else:
                if discretization == DiscretizationType.BDF2:
                    G = (2*dt) / (3*self.component.inductance)
                    Ieq = (4*self.component.discrete_data.lpv1_current - 
                           self.component.discrete_data.lpv2_current)/3
                else:
                    raise ValueError("Specify valid discretization scheme")
            
            # Update A array, assumes A / b passed as references
            A[n1, n1] += G
            A[n2, n2] += G
            A[n1, n2] -= G
            A[n2, n1] -= G
            
            # b vector
            b[n1] -= Ieq
            b[n2] += Ieq
        
        else:
            raise ValueError("Inductor has None or Negative inductance")
    
    def voltage(self):
        raise ValueError("Inductor has no voltage method")

        # self.component.voltage = (self.component.current * 
        #                           self.component.resistance)
        
    def current(self):
        raise ValueError("Inductor has no current method")
        # if self.component.resistance <= 0:
        #     raise ValueError(
        #         f'Error: Resistor {self.component.name} has invalid '
        #         f'resistance: {self.component.resistance}'
        #         )
        
        # self.component.current = (self.component.voltage / 
        #                           self.component.resistance)
        
    def resistance(self):
        raise ValueError("Inductor has no resistance method")
        # if self.component.current == 0:
        #     raise ValueError(
        #         f'Error: Resistor {self.component.name} has invalid '
        #         f'current: {self.component.current}'
        #         )
            
        # self.component.resistance = (self.component.voltage/
        #                              abs(self.component.current))