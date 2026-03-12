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
from typing import Optional

# Custom enums
from enums.component_type import ComponentType
from enums.calculation_mode import CalculationMode
from enums.switch_condition import SwitchCondition
# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

# Ideal component data
@dataclass(slots=True)
class IdealComponentData:
    ideal_voltage: float = 0.0
    ideal_current: float = 0.0
    int_resistance: float = 0.0

# Historical component data
@dataclass(slots=True)
class DiscretizationData:
    lpv1_voltage: float = 0.0
    lpv2_voltage: float = 0.0
    lpv1_current: float = 0.0
    lpv2_current: float = 0.0

@dataclass(slots=True)
class ComponentData:
    # Network information
    name: str
    node1: str
    node2: str
    
    # Physical Properties
    current: float = 0.0
    voltage: float = 0.0
    resistance: float = 0.0
    capacitance: float = 0.0
    inductance: float = 0.0
    
    # Component information
    mode: CalculationMode = CalculationMode.VOLTAGE
    scond: SwitchCondition = SwitchCondition.CLOSED
    ctype: ComponentType = ComponentType.RESISTOR
    
    # Ideal parameters (voltage sources)
    ideal_params: Optional[IdealComponentData] = None
    
    # Discretization data (stores LPVs for derivatives)
    discrete_data: Optional[DiscretizationData] = None