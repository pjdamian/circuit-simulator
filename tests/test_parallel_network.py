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
from enums.component_type import ComponentType
from examples.parallel_network import build_parallel_network

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class TestParallelNetworkPhysics(unittest.TestCase):
    def test_parallel_currents_and_voltages(self):
        # build, solve network
        parallel_net = build_parallel_network()
        parallel_net.solve()
        
        # Get components in network
        voltage_sources = []
        resistors = []
        for n1, n2, data in parallel_net.graph.edges(data=True):
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
        g = 0.0
        for _, _, r in resistors:
            # Ignore connecting wire resistances
            if r.resistance > 1e-9:
                g += 1 / r.resistance
        r_parallel = 1/g if g > 0 else np.inf
        eqv_resistance = r_parallel + voltage_resistance # voltage R
        
        # Calculate expected current
        i_expected = voltage / eqv_resistance
        
        # Check current magnitude through voltage source
        # Sign conventions may not match due to network representation
        self.assertAlmostEqual(abs(voltage_component.current), 
                               abs(i_expected),
                               places=4)
            
        # Check ohms law for resistors (voltage drops)
        for _, _, r in resistors:
            self.assertAlmostEqual(abs(r.voltage), 
                                   abs(r.current * r.resistance),
                                   places=4)
            
        # Check current balance around voltage node (current in = current out)
        node_i = {node: 0.0 for node in parallel_net.graph.nodes}
        for n1, n2, data in parallel_net.graph.edges(data=True):
            c = data['component'].component
            i = getattr(c, 'current', 0.0)
            node_i[n1] -= i
            node_i[n2] += i
        
        # check current balance
        self.assertAlmostEqual(node_i[voltage_n1], 0.0, places=4)


# -----------------------------------------------------------------------------
# Run tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()