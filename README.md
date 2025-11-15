# Circuit Simulator  
*A Python DC network solver using Modified Nodal Analysis (MNA).*

## Overview  
This project implements a modular DC circuit simulator based on **Modified Nodal Analysis (MNA)**.  
It supports arbitrary network topologies using NetworkX and allows simulation of:

- Resistors  
- Voltage sources (with internal resistance)  
- Ideal switches

The solver constructs and solves the MNA system matrix `A x = b`, then returns per-node voltages and per-component currents/voltages for inspection or debugging.

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
- Physics-based validation tests (series & parallel examples)

---

## Example Usage  
Please refer to either "examples/series_network.py" or "examples/parallel_network.py" for examples on how to build networks, and solve them.
