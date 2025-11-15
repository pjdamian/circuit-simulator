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
from components.resistor import Resistor
from data_classes.component_data import ComponentData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class ResistorTests(unittest.TestCase):
    
    def make_test_data(self, **overrides):
        # Default data for tests
        default_data = dict(
            name='R1',
            node1='n1',
            node2='n2',
            current=0.5,
            voltage=0.0,
            resistance=10.0,
            mode=CalculationMode.VOLTAGE,
            scond=SwitchCondition.CLOSED,
            ctype=ComponentType.RESISTOR
            )
        
        # Update default data w/ test specific data
        default_data.update(overrides)
        
        # Return component data class
        return ComponentData(**default_data)
    
    def test_voltage_calculation(self):
        test_data = self.make_test_data()
        resistor = Resistor(test_data)
        resistor.update()
        self.assertEqual(resistor.component.voltage, 5.0)
        
    def test_current_calculation(self):
        test_data = self.make_test_data(
            voltage=10.0,
            resistance=5.0,
            mode=CalculationMode.CURRENT)
        resistor = Resistor(test_data)
        resistor.update()
        self.assertEqual(resistor.component.current, 2.0)
        
    def test_resistance_calculation(self):
        test_data = self.make_test_data(
            voltage=12.0,
            current=4.0,
            mode=CalculationMode.RESISTANCE)
        resistor = Resistor(test_data)
        resistor.update()
        self.assertEqual(resistor.component.resistance, 3.0)
        
    def test_invalid_mode(self):
        test_data = self.make_test_data(mode=None)
        resistor = Resistor(test_data)
        with self.assertRaises(ValueError):
            resistor.update()
            
    def test_invalid_resistance(self):
        test_data = self.make_test_data(
            resistance=0.0,
            mode=CalculationMode.CURRENT)
        resistor = Resistor(test_data)
        with self.assertRaises(ValueError):
            resistor.update()
            
    def test_invalid_current(self):
        test_data = self.make_test_data(
            current=0.0,
            mode=CalculationMode.RESISTANCE)
        resistor = Resistor(test_data)
        with self.assertRaises(ValueError):
            resistor.update()
            
    def test_resistance_negative_i(self):
        test_data =self.make_test_data(
            voltage = 12.0,
            current = -4.0,
            mode=CalculationMode.RESISTANCE)
        resistor = Resistor(test_data)
        resistor.update()
        self.assertEqual(resistor.component.resistance, 3.0)
            
if __name__ == '__main__':
    unittest.main()