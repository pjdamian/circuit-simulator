# -*- coding: utf-8 -*-
"""
Created on Wed Feb 18 07:30:40 2026

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in classes
from typing import Callable, Dict, Optional, Union
import numpy as np
from enums.switch_condition import SwitchCondition

# -----------------------------------------------------------------------------
# Define class
# -----------------------------------------------------------------------------

tfx = Callable[[float], float]
bfx = Callable[[float], bool]

class InputDriver:
    
    def __init__(self, sources={}, states={}):
                
        self.sources: Dict[str, Union[tfx, np.ndarray]] = sources
        self.states: Dict[str, Union[bfx, np.ndarray]] = states
                
    def apply(self, net, t: float, k: Optional[int] = None):
        
        for name, src in self.sources.items():
            comp = net.components_by_name[name].component
            comp.ideal_params.ideal_voltage = float(self._eval(src,t,k))
            
        for name, state in self.states.items():
            comp = net.components_by_name[name].component
            comp_state = bool(self._eval(state, t, k))
            comp.scond = SwitchCondition.CLOSED if comp_state else SwitchCondition.OPEN
    
    @staticmethod
    def _eval(src: Union[tfx, bfx, np.ndarray], t: float, k: Optional[int]):
        
        if callable(src):
            return src(t)
        if k is None:
            raise ValueError("Input Driver: k is a required input for vector driven inputs")
        return float(src[k])
