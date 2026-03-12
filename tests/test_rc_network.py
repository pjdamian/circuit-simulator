# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 06:17:37 2026

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
from examples.rc_network import build_rc_network
from networks.input_driver import InputDriver

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class TestRCNetworkPhysics(unittest.TestCase):
    
    def make_time_vector(self, tau, nsteps=1000):
        """
        Constructs time vector for test cases
        
        Returns
        -------
        Numpy array
            Time vector
        """
        
        # build_rc_network: 2 resistors, 0.1 ohms each, 1 cap at 5.0 F, 
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
        physics = {'V_c': lambda t: v0 * (1-np.exp(-t/tau)),
                   'I_c': lambda t: (v0/r_eq)*(np.exp(-t/tau))}
        
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
        physics = {'V_c': lambda t: v0 * (1-a**k),
                   'I_c': lambda t: (v0/r_eq)*(a**k)}
        return InputDriver(sources=sources), physics 
    
    def make_input_driver_linear(self):
        """
        Note: Will add linear test case later
        
        Returns
        -------
        InputDriver
            Instantiated input driver class to apply inputs to network 
        """
        
        # Constant source
        sources = {'V1': lambda t: 10 + 3*t}
                
        return InputDriver(sources=sources)
    
    def make_input_driver_sin(self, v0, tau, r_eq, w=0, c=0):
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
        coeff = v0/(1+wt2)
        
        physics = {'V_c': lambda t: (coeff*(np.sin(w*t) - 
                                            wt*np.cos(w*t) + 
                                            wt*np.exp(-t/tau))),
                   'I_c': lambda t: (c*w*coeff*(np.cos(w*t) + 
                                                wt*np.sin(w*t) -
                                                np.exp(-t/tau)))}
        
        return InputDriver(sources=sources), physics

    def test_missing_input_driver(self):
        """
        TEST CASE 1: MISSING INPUT TEST CASE, SHOULD RAISE VALUE ERROR

        """
        # build + solve network
        rc_net, r_eq, c = build_rc_network()
        
        with self.assertRaises(ValueError):
            rc_net.solve()    
    
    def test_rc_currents_and_voltages_const_disc(self):
        """
        TEST CASE 2: DISCRETE ANALYTICAL SOLUTION FOR CONSTANT VOLTAGE, SHOULD 
        PASS

        """

        # manually set properties
        v0 = 12             # driving voltage
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-6      # absolute tolerance
        
        # build network, report properties
        rc_net, r_eq, c = build_rc_network()
        tau = r_eq * c
                
        # Generate network inputs
        time = self.make_time_vector(tau)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant_discrete(v0, 
                                                                         tau, 
                                                                         r_eq, 
                                                                         time)

        # build, solve network
        rc_net.solve(time=time, input_driver=input_driver)
        
        # check current (should be the same everywhere)
        for i in range(np.shape(rc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rc_net.sim_data.branch_i[:,i],
                                       physics['I_c'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
        
        # voltage check
        for k, (_, _,c) in enumerate(rc_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.CAPACITOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
    
    def test_rc_currents_and_voltages_const_BE(self):
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
        rc_net, r_eq, c = build_rc_network()
        tau = r_eq * c
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, tau, r_eq)

        # build, solve network
        rc_net.solve(time=time, input_driver=input_driver)
        
        # check current - this does not
        with self.assertRaises(AssertionError):
            for i in range(np.shape(rc_net.sim_data.branch_i)[1]):
                np.testing.assert_allclose(rc_net.sim_data.branch_i[:,i],
                                            physics['I_c'](test_time),
                                            rtol=rel_tol,
                                            atol=abs_tol)        
        
        # voltage check - this passes
        for k, (_, _,c) in enumerate(rc_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.CAPACITOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
    def test_rc_currents_and_voltages_const_BDF2(self):
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
        rc_net, r_eq, c = build_rc_network(discretization=
                                           DiscretizationType.BDF2)
        tau = r_eq * c
                
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, tau, r_eq)

        # build, solve network
        rc_net.solve(time=time, input_driver=input_driver)
        
        # check current - this does not
        for i in range(np.shape(rc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rc_net.sim_data.branch_i[:,i],
                                        physics['I_c'](test_time),
                                        rtol=rel_tol,
                                        atol=abs_tol)        
        
        # voltage check - this passes
        for k, (_, _,c) in enumerate(rc_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.CAPACITOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
    
    def test_rc_currents_and_voltages_AC_BDF2(self):
        """
        TEST CASE 5: ANALYTICAL SOLUTION FOR AC RC circuit, BDF2 FORMULA

        """
        
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-6      # absolute tolerance
                
        # build network, report properties
        rc_net, r_eq, c = build_rc_network(discretization=
                                            DiscretizationType.BDF2)
        tau = r_eq * c
                
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0, 
                                                           tau, 
                                                           r_eq,
                                                           w,
                                                           c)

        # build, solve network
        rc_net.solve(time=time, input_driver=input_driver)
        
        # current check should fail - tolerances too tight
        with self.assertRaises(AssertionError):
            for i in range(np.shape(rc_net.sim_data.branch_i)[1]):
                np.testing.assert_allclose(rc_net.sim_data.branch_i[:,i],
                                            physics['I_c'](test_time),
                                            rtol=rel_tol,
                                            atol=abs_tol)        
        
        # voltage check should fail - tolerances too tight
        with self.assertRaises(AssertionError):
            for k, (_, _,c) in enumerate(rc_net.branch_list):
                # there's only one capacitor in the network
                if c.component.ctype is ComponentType.CAPACITOR:
                    # Making sure this executed
                    # print('Voltage Checked!')
                    np.testing.assert_allclose(rc_net.sim_data.branch_v[:,k],
                                                physics['V_c'](test_time),
                                                rtol=rel_tol,
                                                atol=abs_tol)
                    break

    def test_rc_c_and_v_AC_loose_tol_BDF2(self):
        """
        TEST CASE 6: ANALYTICAL SOLUTION FOR AC RC circuit, BDF2 FORMULA

        """
        
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance

        # build network, report properties
        rc_net, r_eq, c = build_rc_network(discretization=
                                            DiscretizationType.BDF2)
        tau = r_eq * c
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0, 
                                                           tau, 
                                                           r_eq,
                                                           w,
                                                           c)

        # build, solve network
        rc_net.solve(time=time, input_driver=input_driver)
        
        # check current - this does not
        # with self.assertRaises(AssertionError):
        for i in range(np.shape(rc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rc_net.sim_data.branch_i[:,i],
                                        physics['I_c'](test_time),
                                        rtol=rel_tol,
                                        atol=abs_tol)        
        
        # voltage check - this passes
        for k, (_, _,c) in enumerate(rc_net.branch_list):
            # there's only one capacitor in the network
            if c.component.ctype is ComponentType.CAPACITOR:
                # Making sure this executed
                # print('Voltage Checked!')
                np.testing.assert_allclose(rc_net.sim_data.branch_v[:,k],
                                            physics['V_c'](test_time),
                                            rtol=rel_tol,
                                            atol=abs_tol)
                break

# -----------------------------------------------------------------------------
# Run tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()