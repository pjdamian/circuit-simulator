# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 06:22:12 2026

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
from examples.rlc_network import build_rlc_network
from networks.input_driver import InputDriver

# -----------------------------------------------------------------------------
# Define unit test cases
# -----------------------------------------------------------------------------

class TestRLCNetworkPhysics(unittest.TestCase):
    def make_time_vector(self, tau, nsteps=1000):
        """
        Constructs time vector for test cases
        
        Returns
        -------
        Numpy array
            Time vector
        """
        
        return np.linspace(0, 10*tau, nsteps)
    
    def make_input_driver_constant(self, v0, r_eq, r_l, c, w=0):
        """
        Constant voltage case
        
        Inputs
        ------
        v0:     Applied voltage
        tau:    RC time constant
        r_eq:   Equivalent resistance (assuming series config.)
        r_l:    Inductor inductance
        c:      Capacitor capacitance
        w:      Frequency (AC circuit)
        
        Returns
        -------
        InputDriver
            Instantiated input driver class to apply inputs to network 
        """
        
        # Constant source
        sources = {'V1': lambda t: v0 + w*t}
        
        # 3 types of analytical solutions, underdamped, overdamped, 
        # critically damped - depends on physical properties

        w0 = 1/np.sqrt(r_l * c)
        alpha = r_eq / (2*r_l)
        
        if alpha < w0:
            # underdamped
            # print('Step - Underdamped')
            wd = np.sqrt(w0**2 - alpha**2)

            physics = {'V_l': lambda t: (v0 * 
                                         np.exp(-alpha*t) * 
                                         (np.cos(wd*t) - 
                                          (alpha/wd) * np.sin(wd*t))),
                       'V_c': lambda t: (v0 * 
                                         (1 - 
                                          np.exp(-alpha*t) * 
                                          (np.cos(wd*t) + 
                                           (alpha/wd) * np.sin(wd*t)))),
                       'I_rlc': lambda t: ((v0/(r_l*wd)) * 
                                           (np.exp(-alpha*t)) * 
                                           (np.sin(wd*t)))}

        elif alpha > w0:
            # overdamped
            # print('Step - Overdamped')
            beta = np.sqrt(alpha**2 - w0**2)

            physics = {'V_l': lambda t: (v0 * 
                                         np.exp(-alpha*t) * 
                                         (np.cosh(beta*t) - 
                                          (alpha/beta)*np.sinh(beta*t))),
                       'V_c': lambda t: (v0 *
                                         (1 - 
                                          np.exp(-alpha*t) *
                                          (np.cosh(beta*t) + 
                                           (alpha/beta)*np.sinh(beta*t)))),
                       'I_rlc': lambda t: ((v0/(r_l*beta)) * 
                                           np.exp(-alpha*t) *
                                           np.sinh(beta*t))}

        else:
            # critically damped
            # print('Step - Critically damped')
            physics = {'V_l': lambda t: (v0 * 
                                         np.exp(-alpha*t)*(1-alpha*t)),
                       'V_c': lambda t: (v0 * 
                                         (1 - 
                                          np.exp(-alpha*t) * 
                                          (1+alpha*t))),
                       'I_rlc': lambda t: ((v0/r_l) * 
                                           t * 
                                           np.exp(-alpha*t))}
        
        return InputDriver(sources=sources), physics
    
    def make_input_driver_sin(self, v0, r_eq, r_l, c, w=0):
        """
        Note: Will add AC test case later

        Returns
        -------
        InputDriver
            Instantiated input driver class to apply inputs to network
        """
        
        # Periodic source
        sources = {'V1': lambda t: v0*np.sin(w*t)}
        
        # 3 types of analytical solutions, underdamped, overdamped, 
        # critically damped - depends on physical properties

        w0 = 1/np.sqrt(r_l * c)
        alpha = r_eq / (2*r_l)

        if alpha < w0:
            # underdamped
            # print('Step - Underdamped')
            wd = np.sqrt(w0**2 - alpha**2)
            x = w*r_l - 1/(w*c)
            d = r_eq**2 + x**2
            
            v0_d = v0/d
            
            # current
            a = v0*r_eq/d
            b = -v0*x/d
            m = -b
            n = (alpha*m-w*a)/wd
            
            # capacitor
            yc = 1-r_l*c*(w**2)
            dc = yc**2 + (w*r_eq*c)**2
            ac = v0*yc/dc
            bc = -v0*w*r_eq*c/dc
            mc = -bc
            nc = (alpha*mc - w*ac)/wd
            
            physics = {'V_l': lambda t: ((r_l*w*a)*np.cos(w*t) - 
                                         (r_l*w*b)*np.sin(w*t) + 
                                         r_l*np.exp(-alpha*t)*
                                         ((-alpha*m + wd*n)*np.cos(wd*t) + 
                                         (-alpha*n - wd*m)*np.sin(wd*t))),
                       'V_c': lambda t: (ac*np.sin(w*t) + bc*np.cos(w*t) + 
                                         np.exp(-alpha*t) * 
                                         (mc*np.cos(wd*t) + nc*np.sin(wd*t))),
                       'I_rlc': lambda t: (a*np.sin(w*t) + b*np.cos(w*t) + 
                                           np.exp(-alpha*t) * 
                                           (m*np.cos(wd*t) + 
                                            n*np.sin(wd*t)))}

        elif alpha > w0:
            # overdamped
            # print('Step - Overdamped')
            beta = np.sqrt(alpha**2 - w0**2)
            
            # current
            x = w*r_l - 1/(w*c)
            d_i = r_eq**2 + x**2
            m_i = v0*x/d_i
            n_i = (alpha*m_i - w*(v0*r_eq/d_i))/beta
            v0_d = v0/d_i
            
            # capacitor voltages
            y = 1 - r_l * c * (w**2)
            d_c = y**2 + (w*r_eq*c)**2
            m_c = (v0*w*r_eq*c)/d_c
            n_c = (alpha*m_c - w*(v0*y/d_c))/beta
            v0_dc = v0/d_c
            
            # inductor quantities
            a_ind = v0_d*r_eq
            b_ind = -v0_d*x
            m_ind = -b_ind
            n_ind = (alpha*m_ind - w*a_ind)/beta

            physics = {'V_l': lambda t: ((r_l*w*a_ind)*np.cos(w*t) -
                                         (r_l*w*b_ind)*np.sin(w*t) + 
                                         r_l*np.exp(-alpha*t) * 
                                         ((-alpha*m_ind + beta*n_ind) * 
                                          np.cosh(beta*t) + 
                                          (-alpha*n_ind + beta*m_ind) * 
                                          np.sinh(beta*t))),
                       'V_c': lambda t: ((v0_dc*y)*np.sin(w*t) - 
                                         (v0_dc*w*r_eq*c)*np.cos(w*t) + 
                                         np.exp(-alpha*t) * 
                                         (m_c*np.cosh(beta*t) + 
                                          n_c*np.sinh(beta*t))),
                       'I_rlc': lambda t: ((v0_d*r_eq)*np.sin(w*t) - 
                                           (v0_d*x)*np.cos(w*t) + 
                                           np.exp(-alpha*t) * 
                                           (m_i*np.cosh(beta*t) + 
                                            n_i*np.sinh(beta*t)))}
        else:
            # critically damped
            # print('Step - Critically damped')
            x = w*r_l - 1/(w*c)
            d = r_eq**2 + x**2
            a = v0*r_eq / d
            b = -v0*x/d
            m = -b
            n = -w*a - alpha*b
            
            # capacitor quantities
            yc = 1 - r_l * c * (w**2)
            dc = yc**2 + (w*r_eq*c)**2
            ac = v0*yc/dc
            bc = -v0*w*r_eq*c/dc
            mc = -bc
            nc = -w*ac - alpha*bc
            
            physics = {'V_l': lambda t: ((r_l*w*a)*np.cos(w*t) - 
                                         (r_l*w*b)*np.sin(w*t) + 
                                         r_l*np.exp(-alpha*t)*
                                         ((n-alpha*m)-alpha*n*t)),
                       'V_c': lambda t: (ac*np.sin(w*t) + bc*np.cos(w*t) + 
                                         np.exp(-alpha*t) * (mc+nc*t)),
                       'I_rlc': lambda t: (a*np.sin(w*t) + b*np.cos(w*t) + 
                                           np.exp(-alpha*t) * (m + n*t))}
        
        return InputDriver(sources=sources), physics
    
    def test_rlc_c_and_v_const_underdamped_bdf2(self):
        """
        TEST CASE 1: CONSTANT DRIVING VOLTAGE - UNDERDAMPED
        
        """
        
        # manually set properties
        v0 = 12             # driving voltage
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rlc_net, r_eq, rlc_l, c = build_rlc_network(discretization=
                                                    DiscretizationType.BDF2,
                                                    eqv_resistance=1.0,
                                                    inductance=2.0,
                                                    capacitance=2.0)
        
        tau = 2*rlc_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, 
                                                                r_eq,
                                                                rlc_l,
                                                                c)
        
        # solve network
        rlc_net.solve(time=time, input_driver=input_driver)
        
        # current check
        for i in range(np.shape(rlc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rlc_net.sim_data.branch_i[:,i],
                                       physics['I_rlc'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
            
        # capacitor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.CAPACITOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
        # inductor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.INDUCTOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
    def test_rlc_c_and_v_const_overdamped_bdf2(self):
        """
        TEST CASE 2: CONSTANT DRIVING VOLTAGE - OVERDAMPED
        
        """
        
        # manually set properties
        v0 = 12             # driving voltage
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rlc_net, r_eq, rlc_l, c = build_rlc_network(discretization=
                                                    DiscretizationType.BDF2,
                                                    eqv_resistance=4.0,
                                                    inductance=2.0,
                                                    capacitance=2.0)
        
        tau = 2*rlc_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, 
                                                                r_eq,
                                                                rlc_l,
                                                                c)
        
        # solve network
        rlc_net.solve(time=time, input_driver=input_driver)
        
        # current check
        for i in range(np.shape(rlc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rlc_net.sim_data.branch_i[:,i],
                                       physics['I_rlc'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
            
        # capacitor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.CAPACITOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
        # inductor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.INDUCTOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break

    def test_rlc_c_and_v_const_critdamped_bdf2(self):
        """
        TEST CASE 3: CONSTANT DRIVING VOLTAGE - CRITICALLY DAMPED
        
        """
        
        # manually set properties
        v0 = 12             # driving voltage
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rlc_net, r_eq, rlc_l, c = build_rlc_network(discretization=
                                                    DiscretizationType.BDF2,
                                                    eqv_resistance=2.0,
                                                    inductance=2.0,
                                                    capacitance=2.0)
        
        tau = 2*rlc_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_constant(v0, 
                                                                r_eq,
                                                                rlc_l,
                                                                c)
        
        # solve network
        rlc_net.solve(time=time, input_driver=input_driver)
        
        # current check
        for i in range(np.shape(rlc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rlc_net.sim_data.branch_i[:,i],
                                       physics['I_rlc'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
            
        # capacitor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.CAPACITOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
        # inductor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.INDUCTOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
    def test_rlc_c_and_v_ac_underdamped_bdf2(self):
        """
        TEST CASE 4: SIN DRIVING VOLTAGE - UNDER-DAMPED
        
        """
        
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rlc_net, r_eq, rlc_l, c = build_rlc_network(discretization=
                                                    DiscretizationType.BDF2,
                                                    eqv_resistance=1.0,
                                                    inductance=2.0,
                                                    capacitance=2.0)
        
        tau = 2*rlc_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0,
                                                           r_eq,
                                                           rlc_l,
                                                           c,
                                                           w)
        
        # solve network
        rlc_net.solve(time=time, input_driver=input_driver)
        
        # current check
        for i in range(np.shape(rlc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rlc_net.sim_data.branch_i[:,i],
                                       physics['I_rlc'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
            
        # capacitor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.CAPACITOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
        # inductor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.INDUCTOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
    
    def test_rlc_c_and_v_ac_overdamped_bdf2(self):
        """
        TEST CASE 5: SIN DRIVING VOLTAGE - OVER-DAMPED
        
        """
        
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rlc_net, r_eq, rlc_l, c = build_rlc_network(discretization=
                                                    DiscretizationType.BDF2,
                                                    eqv_resistance=4.0,
                                                    inductance=2.0,
                                                    capacitance=2.0)
        
        tau = 2*rlc_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0,
                                                           r_eq,
                                                           rlc_l,
                                                           c,
                                                           w)
        
        # solve network
        rlc_net.solve(time=time, input_driver=input_driver)
        
        # current check
        for i in range(np.shape(rlc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rlc_net.sim_data.branch_i[:,i],
                                       physics['I_rlc'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
            
        # capacitor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.CAPACITOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
        # inductor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.INDUCTOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
    
    def test_rlc_c_and_v_ac_critdamped_bdf2(self):
        """
        TEST CASE 6: SIN DRIVING VOLTAGE - CRITICALLY DAMPED
        
        """
        
        # manually set properties
        v0 = 12             # driving voltage
        w = 60              # driving frequency
        t_steps = 100000    # number of timestamps
        rel_tol = 1e-4      # relative tolerance
        abs_tol = 1e-4      # absolute tolerance
        
        # build network, report properties
        rlc_net, r_eq, rlc_l, c = build_rlc_network(discretization=
                                                    DiscretizationType.BDF2,
                                                    eqv_resistance=2.0,
                                                    inductance=2.0,
                                                    capacitance=2.0)
        
        tau = 2*rlc_l/r_eq
        
        # Generate network inputs
        time = self.make_time_vector(tau, t_steps)
        test_time = time[1:]
        input_driver, physics = self.make_input_driver_sin(v0,
                                                           r_eq,
                                                           rlc_l,
                                                           c,
                                                           w)
        
        # solve network
        rlc_net.solve(time=time, input_driver=input_driver)
        
        # current check
        for i in range(np.shape(rlc_net.sim_data.branch_i)[1]):
            np.testing.assert_allclose(rlc_net.sim_data.branch_i[:,i],
                                       physics['I_rlc'](test_time),
                                       rtol=rel_tol,
                                       atol=abs_tol)
            
        # capacitor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.CAPACITOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_c'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break
            
        # inductor voltage check
        for k, (_, _, m) in enumerate(rlc_net.branch_list):
            if m.component.ctype == ComponentType.INDUCTOR:
                np.testing.assert_allclose(rlc_net.sim_data.branch_v[:,k],
                                           physics['V_l'](test_time),
                                           rtol=rel_tol,
                                           atol=abs_tol)
                break

    
# -----------------------------------------------------------------------------
# Run tests
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()