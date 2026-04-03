# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 08:30:24 2026

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in modules
from dataclasses import dataclass
from typing import Optional

# Custom modules
from enums.discretization_type import DiscretizationType

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

@dataclass
class StampContext:
    dt: Optional[float] = None
    default_dt: bool = True
    discretization: DiscretizationType = DiscretizationType.BACKWARD_EULER
    voltage_source_index: Optional[int] = None