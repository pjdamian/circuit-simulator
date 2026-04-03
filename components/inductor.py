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
from data_classes.stamp_context import StampContext

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
    
        pass
        
    def stamp(self, A, b, n1, n2, ctx: StampContext):
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
        ctx : StampContext, custom data class
            Additional calculation information for capacitors, inductors, 
            voltage sources, etc.

        Raises
        ------
        ValueError
            Capacitor has None or Negative Capacitance. Cap

        Returns
        -------
        None.

        """

        # Used for matrix formulation in network class
        
        if ctx.dt is None:
            raise ValueError("Invalid dt for Inductor calculation")
        
        if (self.component.inductance is not None and
            self.component.inductance > 0):

            # Calculate stamping quantities
            if ((ctx.discretization == DiscretizationType.BACKWARD_EULER) or 
                ctx.default_dt):
                G = ctx.dt / self.component.inductance
                Ieq = self.component.discrete_data.lpv1_current
            else:
                if ctx.discretization == DiscretizationType.BDF2:
                    G = (2*ctx.dt) / (3*self.component.inductance)
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
    
    def post_solve(self, voltage_new: float, ctx: StampContext):
        
        self.component.voltage = voltage_new
        
        if ((ctx.discretization == DiscretizationType.BACKWARD_EULER) or 
            ctx.default_dt):
            
            lpv1_current = self.component.discrete_data.lpv1_current
            
            self.component.current = ((ctx.dt / self.component.inductance) * 
                                      voltage_new + lpv1_current)
        
        elif ctx.discretization == DiscretizationType.BDF2:

            lpv1_current = self.component.discrete_data.lpv1_current
            lpv2_current = self.component.discrete_data.lpv2_current
            
            self.component.current = (((4*lpv1_current - lpv2_current)/3) + 
                                      ((2*ctx.dt) / 
                                       (3*self.component.inductance)) * 
                                      voltage_new)

        # Store lpvs
        self._store_lpv()
                                      
    def voltage(self):
        raise ValueError("Inductor has no voltage method")
        
    def current(self):
        raise ValueError("Inductor has no current method")
        
    def resistance(self):
        raise ValueError("Inductor has no resistance method")
