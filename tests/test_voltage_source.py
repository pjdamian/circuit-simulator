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
from components.voltage_source import VoltageSource
from data_classes.component_data import ComponentData
from data_classes.component_data import IdealComponentData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class VoltageSourceTests(unittest.TestCase):
    
    def make_test_data(self, **overrides):
        
        # Make ideal parameters
        ideal_params = IdealComponentData(
            ideal_voltage=12.0,
            int_resistance=2.0
            )
        
        # Default data for tests
        default_data = dict(
            name='V1',
            node1='n1',
            node2='n2',
            current=1.0,
            voltage=0.0,
            resistance=None,
            mode=CalculationMode.VOLTAGE,
            scond=SwitchCondition.CLOSED,
            ctype=ComponentType.VOLTAGE_SOURCE,
            ideal_params=ideal_params
            )
        
        # Update default data w/ test specific data
        default_data.update(overrides)
        
        # Return component data class
        return ComponentData(**default_data)
    
    def test_voltage_calculation(self):
        """
        TEST 1: CHECKS VOLTAGE CALCULATION, SHOULD PASS
        
        """
        test_data = self.make_test_data()
        vsource = VoltageSource(test_data)
        vsource.update()
        self.assertEqual(vsource.component.voltage, 10.0)
        
    def test_current_calculation(self):
        """
        TEST 2: CHECKS CURRENT CALCULATION, SHOULD PASS
        
        """
        test_data = self.make_test_data(
            voltage=10.0,
            mode=CalculationMode.CURRENT)
        vsource = VoltageSource(test_data)
        vsource.update()
        self.assertEqual(vsource.component.current, 1.0)
        
    def test_resistance_calculation(self):
        """
        TEST 3: CHECKS RESISTANCE CALCULATION, SHOULD PASS

        """
        test_data = self.make_test_data(
            voltage=10.0,
            current=1.0,
            mode=CalculationMode.RESISTANCE)
        vsource = VoltageSource(test_data)
        vsource.update()        
        self.assertEqual(vsource.component.resistance, 2.0)
        
    def test_invalid_mode(self):
        """
        TEST 4: CHECKS INVALID VOLTAGE CALCULATION MODE, SHOULD PASS
        
        """
        test_data = self.make_test_data(mode=None)
        vsource = VoltageSource(test_data)
        with self.assertRaises(ValueError):
            vsource.update()
            
    def test_invalid_internal_resistance(self):
        """
        TEST 5: CHECKS INVALID INTERNAL RESISTANCE, SHOULD PASS

        """
        test_data = self.make_test_data(
            ideal_params=IdealComponentData(ideal_voltage=12.0, 
                                            int_resistance=0.0),
            resistance=0.0,
            mode=CalculationMode.CURRENT)
        vsource = VoltageSource(test_data)
        with self.assertRaises(ValueError):
            vsource.update()
            
    def test_invalid_current(self):
        """
        TEST 6: CHECKS INVALID CURRENT, SHOULD PASS

        """
        test_data = self.make_test_data(
            current=0.0,
            mode=CalculationMode.RESISTANCE)
        vsource = VoltageSource(test_data)
        with self.assertRaises(ValueError):
            vsource.update()
            
    def test_resistance_negative_i(self):
        """
        TEST 7: CHECKS NEGATIVE CURRENT, SHOULD PASS
        
        """
        test_data =self.make_test_data(
            voltage = 10.0,
            current = -1.0,
            mode=CalculationMode.RESISTANCE)
        vsource = VoltageSource(test_data)
        vsource.update()
        self.assertEqual(vsource.component.resistance, 2.0)
            
if __name__ == '__main__':
    unittest.main()