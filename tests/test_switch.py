# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 20:11:00 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built in
import unittest

# Custom classes
from components.switch import Switch
from data_classes.component_data import ComponentData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class SwitchTests(unittest.TestCase):
    
    def make_test_data(self, **overrides):
        # Default data for tests
        default_data = dict(
            name='S1',
            node1='n1',
            node2='n2',
            current=1.0,
            voltage=0.0,
            resistance=0.0,
            mode=CalculationMode.VOLTAGE,
            scond=SwitchCondition.CLOSED,
            ctype=ComponentType.SWITCH
            )
        
        # Update default data w/ test specific data
        default_data.update(overrides)
        
        # Return component data class
        return ComponentData(**default_data)
    
    def test_voltage_closed_switch(self):
        test_data = self.make_test_data()
        switch = Switch(test_data)
        switch.update()
        self.assertAlmostEqual(switch.component.voltage, 1.0e-10)
        
    def test_voltage_open_switch(self):
        test_data = self.make_test_data(
            current=0.001,
            mode=CalculationMode.VOLTAGE,
            scond=SwitchCondition.OPEN)
        switch = Switch(test_data)
        switch.update()
        self.assertAlmostEqual(switch.component.voltage, 1.0e7)
        
    def test_current_closed_switch(self):
        test_data = self.make_test_data(
            voltage=1.0,
            mode=CalculationMode.CURRENT)
        switch = Switch(test_data)
        switch.update()
        self.assertAlmostEqual(switch.component.current, 1.0e10)
        
    def test_current_open_switch(self):
        test_data = self.make_test_data(
            voltage=1.0,
            mode=CalculationMode.CURRENT,
            scond=SwitchCondition.OPEN)
        switch = Switch(test_data)
        switch.update()
        self.assertAlmostEqual(switch.component.current, 1.0e-10)
    
    def test_invalid_mode(self):
        test_data = self.make_test_data(mode=None)
        switch = Switch(test_data)
        with self.assertRaises(ValueError):
            switch.update()
            
    def test_invalid_switch_condition(self):
        test_data = self.make_test_data(
            scond=None,
            mode=CalculationMode.VOLTAGE)
        switch = Switch(test_data)
        with self.assertRaises(ValueError):
            switch.update()
            

            
if __name__ == '__main__':
    unittest.main()