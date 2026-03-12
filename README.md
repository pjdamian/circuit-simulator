# Circuit Simulator  
*A Python DC network solver using Modified Nodal Analysis (MNA).*

## Overview  
This project implements a modular circuit simulator based on **Modified Nodal Analysis (MNA)**.  
It supports arbitrary network topologies using NetworkX and allows simulation of steady state and transient behavior for:

- Resistors  
- Voltage sources (with internal resistance)  
- Ideal switches
- Capacitors
- Inductors

The solver constructs and solves the MNA system matrix `A x = b`, then returns per-node voltages and per-component currents/voltages for inspection or debugging. Two discretization schemes are available and can be specified on network creation - the Backward Euler and 2nd order backward differencing schemes. In many cases, it will be preferable to use the 2nd order scheme to allow larger timesteps for a given simulation.

This project is designed to demonstrate engineering fundamentals in numerical methods, circuit simulation, object-oriented design, and structured testing. 

---

## Features  
- Build networks via `add_node()` and `add_component()`  
- Full MNA stamping for:
  - Resistors (conductance form)  
  - Voltage sources (with additional current unknowns)  
  - Switches (open/closed resistance modeling)  
- Automatic node indexing and isolated-node removal  
- Ground selection and matrix conditioning  
- Node voltage reporting  
- Branch voltage & current reporting with clear sign conventions  
- Physics-based validation tests (series, parallel, RC, RL, RLC circuits)

---

## Example Usage  
Please refer to any of the example networks in the "examples" directory. These scripts show how to build networks and solve them.

## Global Verification
A helper test script was implemented, "run_all_tests.py". This script runs all available tests in the "tests" folder. These include implementation checks, and physics based verification checks. The physics for the example circuits are either trivially simple (series, parallel), or well known problems (RC, RL, and RLC). Analytical equations can be readily found on the web.
