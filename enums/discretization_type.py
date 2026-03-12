# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 19:12:43 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in
from enum import Enum

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

class DiscretizationType(Enum):
    BACKWARD_EULER = 'Backward Euler'
    BDF2 = 'Backward Difference Formula 2'