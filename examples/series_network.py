# -*- coding: utf-8 -*-
"""
Created on Sat Sep 27 22:00:25 2025

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Built-in
from copy import deepcopy

# Custom modules
from networks.network import Network
from components.resistor import Resistor
from components.voltage_source import VoltageSource
from data_classes.component_data import ComponentData, IdealComponentData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition


# -----------------------------------------------------------------------------
# Make simple network
# -----------------------------------------------------------------------------

def build_series_network():
    # Define component data
    resistor_data = ComponentData(
        name='R1',
        node1='n1',
        node2='n2',
        resistance=10,
        voltage=0,
        current=0,
        mode=CalculationMode.VOLTAGE,
        scond=SwitchCondition.CLOSED,
        ctype=ComponentType.RESISTOR)
    
    voltage_data = ComponentData(
        name='V1',
        node1='n0',
        node2='n1',
        resistance=None,
        voltage=10,
        current=0,
        mode=CalculationMode.CURRENT,
        scond=SwitchCondition.CLOSED,
        ctype=ComponentType.VOLTAGE_SOURCE,
        ideal_params=IdealComponentData(ideal_voltage=12,
                                        int_resistance=1))
    
    # Generate network
    series_net = Network(node_reporting=False,
                         branch_reporting=True)
    
    # Add nodes
    series_net.add_node('n0')
    series_net.add_node('n1')
    series_net.add_node('n2')
    series_net.add_node('n3')
    
    # Add components
    series_net.add_component('n0','n1',VoltageSource(voltage_data))
    series_net.add_component('n1','n2',Resistor(resistor_data))
    series_net.add_component('n2','n3',Resistor(deepcopy(resistor_data)))
    series_net.add_component('n3','n0',Resistor(deepcopy(resistor_data)))
    
    # # Solve network
    # series_net.solve()
    
    return series_net
    
    
if __name__ == '__main__':
    series_net = build_series_network()
    series_net.solve()
