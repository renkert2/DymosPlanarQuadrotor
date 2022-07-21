# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 14:55:59 2022

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import os
import DynamicModel as DM

g = 9.80665

class PlanarController(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        ### Controller Parameters (Static)
        self.add_input("k_p_r", shape=(1,), val=1, desc="Position Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_d_r", shape=(1,), val=1, desc="Position Derivative Gain", tags=['dymos.static_target'])
        self.add_input("k_p_theta", shape=(1,), val=1, desc="Angle Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_p_omega", shape=(1,), val=1, desc="Rotor Speed Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_i_omega", shape=(1,), val=1, desc="Rotor Speed Integral Gain", tags=['dymos.static_target'])

        ### Other Parameters (Static)
        self.add_input('Mass__System', shape = (1,), val=1, desc='mass', units='kg', tags=['dymos.static_target'])
        self.add_input('r__Frame', shape = (1,), val=0.1, desc='arm length', units='m', tags=['dymos.static_target'])
        self.add_input('K_T__Propeller', shape=(1,), val=1, desc="Lumped Thrust Coefficient", tags=['dymos.static_target'])
        
        ### Dynamic Inputs
        self.add_input("x_T", shape=(nn,), desc="x reference trajectory", units='m')
        self.add_input("y_T", shape=(nn,), desc="y reference trajectory", units='m')
        
        self.add_input("x_T_dot", shape=(nn,), desc="x reference velocity", units='m/s')
        self.add_input("y_T_dot", shape=(nn,), desc="y reference velocity", units='m/s')
        
        self.add_input("omega_1", shape=(nn,), desc="Right rotor velocity", units='rad/s')
        self.add_input("omega_2", shape=(nn,), desc="Left rotor velocity", units='rad/s')

        ### Dynamic Outputs
        self.add_output("u_1", shape=(nn,), desc="Inverter 1 Input")
        self.add_output("u_2", shape=(nn,), desc="Inverter 2 Input")

        # Controller States        
        self.add_output("e_omega_1", shape=(nn,), desc="Rotor speed 1 error")
        self.add_output("e_omega_2", shape=(nn,), desc="Rotor speed 2 error")
        
        self.add_input("e_omega_1_I", shape=(nn,), desc="Rotor speed 1 error integral")
        self.add_input("e_omega_2_I", shape=(nn,), desc="Rotor speed 2 error integral")
        
        ### Declare Partials
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])
        
        # Use self._var_rel2meta (or self._static_var_rel2meta) dictionary to get all inputs and outputs; check shape field to differentiate inputs from outputs
    def compute(self, inputs, outputs):
        
        
    def compute_partials(self, inputs, partials):
        
        
    def ModifyPhase(phase, openmdao_path=""):
        
    def ModifyTraj(traj, openmdao_path="")