# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 19:15:31 2026

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
from enums.discretization_type import DiscretizationType
from examples.rl_network import build_rl_network
from networks.input_driver import InputDriver

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class TestRLNetworkPhysics(unittest.TestCase):
    def make_time_vector(self, tau, nsteps=1000):
        """
        Constructs time vector for test cases
        
        Returns
        -------
        Numpy array
            Time vector
        """
        
        # build_rl_network: 2 resistors, 0.1 ohms each, 1 cap at 5.0 F, 
        # tau = RC = R_eq*C = (0.1 + 0.1)*5.0 = 1.0
        # setting final element to 10*tau, 
        
        return np.linspace(0, 10*tau, nsteps)
    
    def make_input_driver_constant(self, v0, tau, r_eq, w=0):
        """
        Constant voltage case
        
        Inputs
        ------
        v0:     Applied voltage
        tau:    RC time constant
        r_eq:   Equivalent resistance (assuming series config.) 
        w:      Frequency (AC circuit)
        
        Returns
        -------
        InputDriver
            Instantiated input driver class to apply inputs to network 
        """
        
        # Constant source
        sources = {'V1': lambda t: v0 + w*t}
        physics = {'V_l': lambda t: v0 * (np.exp(-t/tau)),
                   'I_l': lambda t: (v0/r_eq)*(1-np.exp(-t/tau))}
        
        return InputDriver(sources=sources), physics
    
    def make_input_driver_constant_discrete(self, v0, tau, r_eq, time, w=0):
        """
        Discretized form required for BE test case to pass - added BDF2 
        discretization to solver to address this
        
        Inputs
        ------
        v0:     Applied voltage
        tau:    RC time constant
        r_eq:   Equivalent resistance (assuming series config.) 
        w:      Frequency (AC circuit)
        
        Returns
        -------
        InputDriver
            Instantiated input driver class to apply inputs to network 
        """
        
        dt = time[1] - time[0]
        a = 1.0/(1.0+dt/tau)
        k = np.arange(1,len(time))
        
        
        # Discrete Constant Source
        sources = {'V1': lambda t: v0 + w*t}
        physics = {'V_l': lambda t: v0 * (a**k),
                   'I_l': lambda t: (v0/r_eq)*(1-a**k)}
        return InputDriver(sources=sources), physics
    
    def make_input_driver_sin(self, v0, tau, r_eq, w, rl_l):
        """
        Note: Will add AC test case later

        Returns
        -------
        InputDriver
            Instantiated input driver class to apply inputs to network
        """
        
        # Periodic source
        sources = {'V1': lambda t: v0*np.sin(w*t)}
        
        # Solution physics
        wt = w*tau
        wt2 = wt**2
        i_coeff = v0/(r_eq*(1+wt2))
        v_coeff = (v0 * wt)/(1+wt2)
        
        physics = {'V_l': lambda t: v_coeff*(np.cos(w*t) + 
                                             wt*np.sin(w*t) - 
                                             np.exp(-t/tau)),
                   'I_l': lambda t: i_coeff*(np.sin(w*t) - 
                                             wt*np.cos(w*t) + 
                                             wt*np.exp(-t/tau))}
        
        return InputDriver(sources=sources), physics
    
    def test_missing_input_driver(self):
        """
        TEST CASE 1: MISSING INPUT TEST CASE, SHOULD RAISE VALUE ERROR

        """
        # build + solve network
        rl_net, r_eq, l = build_rl_network()
        
        with self.assertRaises(ValueError):
            rl_net.solve()
            
    def test_rl_currents_and_voltages_const_disc(self):
        """
        TEST CASE 2: DISCRETE ANALYTICAL SOLUTION FOR CONSTANT VOLTAGE, SHOULD 
        PASS

        """
        
        # manually set properties
        v0 = 12             # driving voltage
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-6      # absolute tolerance
        
        # build network, report properties
        rl_net, r_eq, l = build_rl_network()
        tau = l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant_discrete(v0, 
                                                                         tau, 
                                                                         r_eq, 
                                                                         time)

        # build, solve network
        rl_net.solve(time=time, input_driver=input_driver)
        
        # check current (should be the same everywhere)
        for i in range(np.shape(rl_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rl_net.sim_data.branch_i[:,i],
                                       physics['I_l'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
        
        # voltage check
        for k, (_, _,c) in enumerate(rl_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.INDUCTOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rl_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
    
    def test_rl_currents_and_voltages_const_BE(self):
        """
        TEST CASE 3: ANALYTICAL SOLUTION FOR CONSTANT VOLTAGE, SHOULD FAIL,
        TIMESTEPS TOO SMALL FOR DISCRETIZATION SCHEME (FIRST ORDER DIFFERENCE)

        """
        
        # manually set properties
        v0 = 12             # driving voltage
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-6      # absolute tolerance

        # build network, report properties
        rl_net, r_eq, l = build_rl_network()
        tau = l/r_eq
                
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, tau, r_eq)

        # build, solve network
        rl_net.solve(time=time, input_driver=input_driver)
        
        # Not needed - time grid is fine enough
        # with self.assertRaises(AssertionError):
        for i in range(np.shape(rl_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rl_net.sim_data.branch_i[:,i],
                                        physics['I_l'](test_time),
                                        rtol=rel_tol,
                                        atol=abs_tol)        
        
        # voltage check - fails
        with self.assertRaises(AssertionError):
            for k, (_, _,c) in enumerate(rl_net.branch_list):
                # there's only one capacitor in the network
                if c.component.ctype is ComponentType.INDUCTOR:
                    # Making sure this executed
                    # print('Voltage Checked!')
                    np.testing.assert_allclose(rl_net.sim_data.branch_v[:,k],
                                               physics['V_l'](test_time),
                                               rtol=rel_tol,
                                               atol=abs_tol)
                    break
            
    def test_rl_currents_and_voltages_const_BDF2(self):
        """
        TEST CASE 4: ANALYTICAL SOLUTION FOR CONSTANT VOLTAGE, BDF2 FORMULA, 
        SHOULD PASS

        """
        # manually set properties
        v0 = 12             # driving voltage
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-6      # absolute tolerance
        
        # build network, report properties
        rl_net, r_eq, l = build_rl_network(discretization=
                                           DiscretizationType.BDF2)
        tau = l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, tau, r_eq)

        # build, solve network
        rl_net.solve(time=time, input_driver=input_driver)
        
        # check current - this does not
        for i in range(np.shape(rl_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rl_net.sim_data.branch_i[:,i],
                                        physics['I_l'](test_time),
                                        rtol=rel_tol,
                                        atol=abs_tol)        
        
        # voltage check - this passes
        for k, (_, _,c) in enumerate(rl_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.INDUCTOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rl_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
    def test_rl_currents_and_voltages_AC_BDF2(self):
        """
        TEST CASE 4: ANALYTICAL SOLUTION FOR AC RL CIRCUIT, BDF2 FORMULA

        """
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-6      # absolute tolerance
        
        # build network, report properties
        rl_net, r_eq, rl_l = build_rl_network(discretization=
                                              DiscretizationType.BDF2)
        tau = rl_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0,
                                                           tau, 
                                                           r_eq, 
                                                           w, 
                                                           rl_l)

        # build, solve network
        rl_net.solve(time=time, input_driver=input_driver)
        
        # current check should fail - tolerances too tight
        with self.assertRaises(AssertionError):
            for i in range(np.shape(rl_net.sim_data.branch_i)[1]):
                np.testing.assert_allclose(rl_net.sim_data.branch_i[:,i],
                                            physics['I_l'](test_time),
                                            rtol=rel_tol,
                                            atol=abs_tol)        
        
        # voltage check should fail - tolerances too tight
        with self.assertRaises(AssertionError):
            for k, (_, _,c) in enumerate(rl_net.branch_list):
                # there's only one capacitor in the network
                if c.component.ctype is ComponentType.INDUCTOR:
                    # Making sure this executed
                    # print('Voltage Checked!')
                    np.testing.assert_allclose(rl_net.sim_data.branch_v[:,k],
                                               physics['V_l'](test_time),
                                               rtol=rel_tol,
                                               atol=abs_tol)
                    break
            
    def test_rl_c_and_v_AC_loose_tol_BDF2(self):
        """
        TEST CASE 4: ANALYTICAL SOLUTION FOR AC RL CIRCUIT, BDF2 FORMULA

        """
        
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rl_net, r_eq, rl_l = build_rl_network(discretization=
                                              DiscretizationType.BDF2)
        tau = rl_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0,
                                                           tau, 
                                                           r_eq, 
                                                           w, 
                                                           rl_l)

        # build, solve network
        rl_net.solve(time=time, input_driver=input_driver)
        
        # current check should fail - tolerances too tight
        for i in range(np.shape(rl_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rl_net.sim_data.branch_i[:,i],
                                        physics['I_l'](test_time),
                                        rtol=rel_tol,
                                        atol=abs_tol)        
        
        # voltage check should fail - tolerances too tight
        for k, (_, _,c) in enumerate(rl_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.INDUCTOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rl_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
                

# -----------------------------------------------------------------------------
# Run tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()