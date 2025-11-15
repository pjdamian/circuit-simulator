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
@dataclass
class IdealComponentData:
    ideal_voltage: float = 0.0
    ideal_current: float = 0.0
    int_resistance: float = 0.0

@dataclass
class ComponentData:
    name: str
    node1: str
    node2: str
    current: float
    voltage: float
    resistance: float
    mode: CalculationMode
    scond: SwitchCondition
    ctype: ComponentType
    
    # Ideal parameters
    ideal_params: Optional[IdealComponentData] = None