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

# Third-party
# import math

# Custom modules
from enums.component_type import ComponentType
from examples.series_network import build_series_network

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class TestSeriesNetworkPhysics(unittest.TestCase):
    def test_series_currents_and_voltages(self):
        # build, solve network
        series_net = build_series_network()
        series_net.solve()
        
        # Get components in network
        voltage_sources = []
        resistors = []
        for n1, n2, data in series_net.graph.edges(data=True):
            c = data['component'].component
            if c.ctype == ComponentType.VOLTAGE_SOURCE:
                voltage_sources.append((n1,n2,c))
            elif c.ctype == ComponentType.RESISTOR:
                resistors.append((n1,n2,c))
                
        # Confirm singular voltage source
        self.assertEqual(len(voltage_sources),1)
        voltage_n1, voltage_n2, voltage_component = voltage_sources[0]
        
        # Get parameters
        voltage = voltage_component.ideal_params.ideal_voltage
        voltage_resistance = voltage_component.ideal_params.int_resistance
        
        # Calculate equivalent resistance
        eqv_resistance = sum(r[2].resistance for r in resistors) # resistor R
        eqv_resistance += voltage_resistance # voltage R
        
        # Calculate expected current
        i_expected = voltage / eqv_resistance
        
        # Check current magnitude through voltage source
        # Sign conventions may not match due to network representation
        self.assertAlmostEqual(abs(voltage_component.current), 
                               abs(i_expected),
                               places=4)
        for _, _, r in resistors:
            self.assertAlmostEqual(abs(r.current), 
                                   abs(i_expected),
                                   places=4)
            
        # Check ohms law for resistors (voltage drops)
        for _, _, r in resistors:
            self.assertAlmostEqual(abs(r.voltage), 
                                   abs(r.current * r.resistance),
                                   places=4)


# -----------------------------------------------------------------------------
# Run tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()