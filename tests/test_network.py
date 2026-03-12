# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 22:00:25 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built-in
import unittest
import numpy as np

# Third-party
# import math

# Custom modules
from networks.network import Network
from components.resistor import Resistor
from components.voltage_source import VoltageSource
from data_classes.component_data import ComponentData, IdealComponentData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition


# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class NetworkTests(unittest.TestCase):
    
    def make_resistor(self, name='R1', resistance=10.0, voltage=None, 
                      current=None, mode=CalculationMode.VOLTAGE):
        return Resistor(ComponentData(
            name=name,
            node1='n1',
            node2='n2',
            resistance=resistance,
            voltage=voltage,
            current=current,
            mode=mode,
            ctype=ComponentType.RESISTOR,
            scond=SwitchCondition.CLOSED
        ))
    
    def make_voltage_source(self, name='V1', ideal_voltage=10.0,
                            resistance=None, int_resistance=0.1, 
                            voltage=None, current=None, 
                            mode=CalculationMode.CURRENT):
        return VoltageSource(ComponentData(
            name=name,
            node1='n1',
            node2='n2',
            voltage=voltage,
            current=current,
            resistance=resistance,
            mode=mode,
            ctype=ComponentType.VOLTAGE_SOURCE,
            scond=SwitchCondition.CLOSED,
            ideal_params=IdealComponentData(
                ideal_voltage=ideal_voltage,
                int_resistance=int_resistance
            )
        ))

    def test_add_nodes_and_positions(self):
        """
        TEST 1: CONFIRMS NODES ARE ADDED AND HAVE THE CORRECT POSITIONS

        """
        net = Network()
        net.add_node('A', pos=(0, 0))
        net.add_node('B', pos=(1, 1))
        
        self.assertIn('A', net.graph.nodes)
        self.assertIn('B', net.graph.nodes)
        self.assertEqual(net.graph.nodes['A']['pos'], (0, 0))
        self.assertEqual(net.graph.nodes['B']['pos'], (1, 1))

    def test_add_component(self):
        """
        TEST 2: CONFIRMS COMPONENTS CAN BE ADDED TO THE NETWORK CLASS

        """
        net = Network()
        r = self.make_resistor()
        net.add_node('n1')
        net.add_node('n2')
        net.add_component('n1', 'n2', r)
        
        self.assertIn(('n1', 'n2',r.component.name), net.graph.edges)
        self.assertEqual(net.graph['n1']['n2'][r.component.name]['component'], 
                         r)

    def test_set_mode_propagation(self):
        """
        TEST 3: CONFIRMS MODE IS PROPAGATED FROM NETWORK INSTANTIATION TO 
        COMPONENT

        """
        net = Network()
        r = self.make_resistor(mode=CalculationMode.RESISTANCE)
        v = self.make_voltage_source(mode=CalculationMode.RESISTANCE)
        net.add_node('n1')
        net.add_node('n2')
        net.add_node('n3')
        net.add_component('n1', 'n2', r)
        net.add_component('n2', 'n3', v)
        
        net._set_mode(CalculationMode.CURRENT)
        self.assertEqual(r.component.mode, CalculationMode.CURRENT)
        self.assertEqual(v.component.mode, CalculationMode.CURRENT)

    def test_solve_calls_update(self):
        """
        TEST 4: CONFIRMS NETWORK CAN SOLVE SIMPLE CASE

        """
        net = Network()
        r = self.make_resistor(voltage=5.0)
        r.component.current = None  # Ensure update() calculates current
        net.add_node('n1')
        net.add_node('n2')
        net.add_component('n1', 'n2', r)

        net._set_mode(CalculationMode.CURRENT)
        net.solve()
        
        expected_current = r.component.voltage / r.component.resistance
        self.assertAlmostEqual(r.component.current, expected_current)

    def test_solve_with_time(self):
        """
        TEST 5: CONFIRMS NETWORK CAN SOLVE 1 DT CASE
        
        """
        # Placeholder test for time-dependent sources (if implemented)
        net = Network()
        r = self.make_resistor(voltage=5.0)
        net.add_node('n1')
        net.add_node('n2')
        net.add_component('n1', 'n2', r)
        
        net._set_mode(CalculationMode.CURRENT)
        # Should still work even if time is ignored

        net.solve(time=np.array([0.001])) 
        self.assertIsNotNone(r.component.current)

    def test_missing_nodes_are_handled(self):
        """
        TEST 6: CONFIRMS NODES RENAMED APPROPRIATELY

        """
        net = Network()
        r = self.make_resistor()
        net.add_component('x', 'y', r)
        self.assertIn('x', net.graph.nodes)
        self.assertIn('y', net.graph.nodes)

    def test_invalid_mode_handling(self):
        """
        TEST 7: CONFIRMS INVALID CALCULATION MODE FOR COMPONENTS WORK

        """        
        net = Network()
        r = self.make_resistor(mode=None)
        net.add_node('n1')
        net.add_node('n2')
        net.add_component('n1', 'n2', r)
        
        with self.assertRaises(ValueError):
            net.solve()

# -----------------------------------------------------------------------------
# Run tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()