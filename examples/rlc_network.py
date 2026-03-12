# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 06:15:31 2026

@author: pmdam
"""

# -----------------------------------------------------------------------------
# Import statements
# -----------------------------------------------------------------------------

# Custom modules
from networks.network import Network
from components.resistor import Resistor
from components.voltage_source import VoltageSource
from components.inductor import Inductor
from components.capacitor import Capacitor
from data_classes.component_data import ComponentData, IdealComponentData, DiscretizationData
from enums.calculation_mode import CalculationMode
from enums.component_type import ComponentType
from enums.switch_condition import SwitchCondition
from enums.discretization_type import DiscretizationType

# -----------------------------------------------------------------------------
# Make simple network
# -----------------------------------------------------------------------------

def build_rlc_network(discretization=DiscretizationType.BACKWARD_EULER,
                      eqv_resistance=1, inductance=5.0, capacitance=1.0):
    # Define component data
    resistor_data = ComponentData(
        name='R1',
        node1='n1',
        node2='n2',
        resistance=0.5*eqv_resistance,
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
                                        int_resistance=0.5*eqv_resistance))
    
    # Component Data has a bunch of default values; no other values apply for 
    # capacitors - they do not internally update state. Voltage must be 
    # specified
    inductor_data = ComponentData(
        name='L1', 
        node1='n3', 
        node2='n4',
        resistance=None,
        voltage=0,
        current=0,
        inductance=inductance,
        discrete_data=DiscretizationData())
    
    capacitor_data = ComponentData(
        name='C1', 
        node1='n3', 
        node2='n4',
        resistance=None,
        voltage=0,
        current=0,
        capacitance=capacitance,
        discrete_data=DiscretizationData())
    
    # Generate network
    rlc_net = Network(node_reporting=False,
                      branch_reporting=False,
                      discretization=discretization)
    
    # Add nodes
    rlc_net.add_node('n0')
    rlc_net.add_node('n1')
    rlc_net.add_node('n2')
    rlc_net.add_node('n3')
    
    # Add components
    rlc_net.add_component('n0','n1',VoltageSource(voltage_data))
    rlc_net.add_component('n1','n2',Resistor(resistor_data))
    rlc_net.add_component('n2','n3',Capacitor(capacitor_data))
    rlc_net.add_component('n3','n0',Inductor(inductor_data))
    
    # Calculate equivalent resistance, report capacitance
    r_eq = resistor_data.resistance + voltage_data.ideal_params.int_resistance
    inductance = inductor_data.inductance
    capacitance = capacitor_data.capacitance
    
    return rlc_net, r_eq, inductance, capacitance
    
    
if __name__ == '__main__':
    rlc_net = build_rlc_network()
    rlc_net.solve()