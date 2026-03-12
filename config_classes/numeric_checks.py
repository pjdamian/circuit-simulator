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

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

@dataclass
class MathChecks:
    min_dt: float = 1e-6
    max_conductance: float = 1e9
