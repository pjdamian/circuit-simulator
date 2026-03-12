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
from components.capacitor import Capacitor
from data_classes.component_data import ComponentData, IdealComponentData, DiscretizationData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition
from enums.discretization_type import DiscretizationType

# -----------------------------------------------------------------------------
# Make simple network
# -----------------------------------------------------------------------------

def build_rc_network(discretization=DiscretizationType.BACKWARD_EULER):
    # Define component data
    resistor_data = ComponentData(
        name='R1',
        node1='n1',
        node2='n2',
        resistance=0.1,
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
    
    # Component Data has a bunch of default values; no other values apply for 
    # capacitors - they do not internally update state. Voltage must be 
    # specified
    capacitor_data = ComponentData(
        name='C1', 
        node1='n3', 
        node2='n4',
        resistance=None,
        voltage=0,
        current=0,
        capacitance=5.0,
        discrete_data=DiscretizationData())
    
    # Generate network
    rc_net = Network(node_reporting=False,
                     branch_reporting=False,
                     discretization=discretization)
    
    # Add nodes
    rc_net.add_node('n0')
    rc_net.add_node('n1')
    rc_net.add_node('n2')
    rc_net.add_node('n3')
    
    # Add components
    rc_net.add_component('n0','n1',VoltageSource(voltage_data))
    rc_net.add_component('n1','n2',Resistor(resistor_data))
    rc_net.add_component('n2','n3',Resistor(deepcopy(resistor_data)))
    rc_net.add_component('n3','n0',Capacitor(capacitor_data))
    
    # Calculate equivalent resistance, report capacitance
    r_eq = 2*resistor_data.resistance + voltage_data.ideal_params.int_resistance
    c = capacitor_data.capacitance
    
    return rc_net, r_eq, c
    
    
if __name__ == '__main__':
    rc_net = build_rc_network()
    rc_net.solve()
