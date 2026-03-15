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
- Two discretization schemes: Backward Euler and BDF2. BDF2 provides second-order accuracy allowing larger timesteps for equivalent precision
- Physics-based validation tests (series, parallel, RC, RL, RLC circuits). All transient tests validate against closed form analytical solutions across all damping regimes.

## Example Usage  
See the `examples/` directory for complete RC, RL, and RLC transient simulations.

## Testing
A helper test script was implemented, "run_all_tests.py". This script runs all available tests in the "tests" folder. These include implementation checks, and physics based verification checks. The physics for the example circuits are either trivially simple (series, parallel), or well known problems (RC, RL, and RLC). Analytical equations can be readily found on the web.

---

## Project structure
```
circuit-simulator/
├── components/         # Circuit element classes (Resistor, Capacitor, etc.)
├── config_classes/     # Numerical configuration (min timestep, etc.)
├── data_classes/       # Data containers (ComponentData, NodeData, etc.)
├── enums/              # Enumerations (ComponentType, DiscretizationType, etc.)
├── examples/           # Pre-built example networks (RC, RL, RLC, series, parallel)
├── networks/           # Core solver (Network, InputDriver)
├── tests/              # Physics-based validation test suite
└── run_all_tests.py    # Test runner
```

---

## Installation
```bash
pip install -r requirements.txt
```

---

## Running the tests
```bash
PYTHONPATH=. python run_all_tests.py
```

Expected output: 47 tests, 0 failures.

---
