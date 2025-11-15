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

def build_parallel_network():
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
    
    wire_data = ComponentData(
        name='W1',
        node1='n1',
        node2='n2',
        resistance=1e-10,
        voltage=0,
        current=0,
        mode=CalculationMode.VOLTAGE,
        scond=SwitchCondition.CLOSED,
        ctype=ComponentType.RESISTOR
        )
    
    # Generate network
    parallel_net = Network(node_reporting=False,branch_reporting=True)
    
    # Add nodes
    parallel_net.add_node('n0')
    parallel_net.add_node('n1')
    parallel_net.add_node('n2') # kept to demo node pruning feature
    parallel_net.add_node('n3') # kept to demo node pruning feature
    
    parallel_net.add_node('w1')
    parallel_net.add_node('w2')
    parallel_net.add_node('w3')
    parallel_net.add_node('w4')
    parallel_net.add_node('w5')
    parallel_net.add_node('w6')
    
    # Add components
    
    parallel_net.add_component('n0','n1',VoltageSource(voltage_data))
    
    parallel_net.add_component('n1','w1',Resistor(wire_data))
    parallel_net.add_component('w1','w2',Resistor(deepcopy(wire_data)))
    parallel_net.add_component('w2','w3',Resistor(deepcopy(wire_data)))
    
    parallel_net.add_component('n0','w4',Resistor(deepcopy(wire_data)))
    parallel_net.add_component('w4','w5',Resistor(deepcopy(wire_data)))
    parallel_net.add_component('w5','w6',Resistor(deepcopy(wire_data)))
        
    parallel_net.add_component('w1','w4',Resistor((resistor_data)))
    parallel_net.add_component('w2','w5',Resistor(deepcopy(resistor_data)))
    parallel_net.add_component('w3','w6',Resistor(deepcopy(resistor_data)))
    
    # Solve network
    return parallel_net

if __name__ == '__main__':
    parallel_net = build_parallel_network()
    parallel_net.solve()
