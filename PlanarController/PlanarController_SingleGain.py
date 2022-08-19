# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 14:55:59 2022

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import openmdao.core as omcore
from dymos.utils.misc import _unspecified
import os

from GraphTools_Phil_V2.OpenMDAO import Param as P
import GraphTools_Phil_V2.OpenMDAO.DynamicModel as DM

g = 9.80665

class PlanarControllerParams(P.ParamSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        kw = {"parent":"Controller", "component":"PlanarController"}
        self.add(P.Param(name="k_p_r", val=1, desc="Position Proportional Gain", strID="k_p_r__Controller", **kw))
        self.add(P.Param(name="k_d_r", val=1, desc="Position Derivative Gain", strID="k_d_r__Controller", **kw))
        self.add(P.Param(name="k_p_theta", val=1, desc="Angle Proportional Gain", strID="k_p_theta__Controller", **kw))
        self.add(P.Param(name="k_d_theta", val=1, desc="Angle Derivative Gain", strID="k_d_theta__Controller", **kw))
        self.add(P.Param(name="k_p_omega", val=1, desc="Rotor Speed Proportional Gain", strID="k_p_omega__Controller", **kw))
        self.add(P.Param(name="k_i_omega", val=1, desc="Rotor Speed Integral Gain", strID="k_i_omega__Controller", **kw))
        self.add(P.Param(name="k_b_omega", val=1, desc="Rotor Speed Anti-Windup Gain", strID="k_b_omega__Controller", **kw))
        
class PlanarController(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        shared_args = {"num_nodes":nn}
                
        body_controller = PlanarBodyController(**shared_args)
        self.add_subsystem("body_controller", body_controller, promotes=["*"])
        
        ppt_controller = PlanarPTController(saturate=True, saturation_type="SMOOTH", saturation_constant=10, **shared_args)
        self.add_subsystem("ppt_controller", ppt_controller, promotes=["*"])
        
class PlanarBodyController(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)    
        
    def setup(self):
        nn = self.options["num_nodes"]
        shared_args = {"num_nodes":nn}
        
        for o,i in (("e_p_x", ("x","x_T")), ("e_p_y", ("y", "y_T")),  ("e_v_x", ("v_x","v_x_T")),  ("e_v_y", ("v_y", "v_y_T")), ("e_a_x", ("a_x","a_x_T")),  ("e_a_y", ("a_y", "a_y_T"))):
            c = om.AddSubtractComp(output_name=o, input_names=i, vec_size=nn, scaling_factors=[1,-1])
            self.add_subsystem(o,c,promotes=["*"])
            
        c = calcDesiredForces(**shared_args)
        self.add_subsystem("F_star", c, promotes=["*"])
        
        c = calcDesiredThrust(**shared_args)
        self.add_subsystem("T_star", c, promotes=["*"])
        
        c = calcDesiredTorque(**shared_args)
        self.add_subsystem("tau_z_star", c, promotes=["*"])
        
        c = calcDesiredRotorSpeeds(**shared_args)
        self.add_subsystem("omega_star", c, promotes=["*"])
        
        tracking_error = calcTrackingError(W_x=1.0,W_y=1.0,**shared_args)
        self.add_subsystem("tracking_error", tracking_error, promotes=["*"])

class calcDesiredForces(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
    
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_input("k_p_r__Controller", shape=(1,), val=1, desc="Position Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_d_r__Controller", shape=(1,), val=1, desc="Position Derivative Gain", tags=['dymos.static_target'])
        self.add_input('Mass__System', shape = (1,), val=1, desc='mass', units='kg', tags=['dymos.static_target'])
        
        for i in ("e_p_x", "e_p_y", "e_v_x", "e_v_y", "e_a_x", "e_a_y"):
            self.add_input(i, shape=(nn,))
        
        for o in ("F_star_x", "F_star_y", "F_star_x_dot", "F_star_y_dot"):
            self.add_output(o, shape=(nn,))
        
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])
        
        args = {"rows":arange, "cols":arange}
        self.declare_partials("F_star_x", "e_p_x", method="exact", **args)
        self.declare_partials("F_star_x", "e_p_y", dependent=False, **args)
        self.declare_partials("F_star_x", "e_v_x", method="exact", **args)
        self.declare_partials("F_star_x", "e_v_y", dependent=False, **args)
        self.declare_partials("F_star_x", "e_a_x", dependent=False, **args)
        self.declare_partials("F_star_x", "e_a_y", dependent=False, **args)
        
        self.declare_partials("F_star_y", "e_p_x", dependent=False, **args)
        self.declare_partials("F_star_y", "e_p_y", method="exact", **args)
        self.declare_partials("F_star_y", "e_v_x", dependent=False,**args)
        self.declare_partials("F_star_y", "e_v_y", method="exact", **args)
        self.declare_partials("F_star_y", "e_a_x", dependent=False,**args)
        self.declare_partials("F_star_y", "e_a_y", dependent=False, **args)
        
        self.declare_partials("F_star_x_dot", "e_p_x", dependent=False, **args)
        self.declare_partials("F_star_x_dot", "e_p_y", dependent=False, **args)
        self.declare_partials("F_star_x_dot", "e_v_x", method="exact", **args)
        self.declare_partials("F_star_x_dot", "e_v_y", dependent=False, **args)
        self.declare_partials("F_star_x_dot", "e_a_x", method="exact", **args)
        self.declare_partials("F_star_x_dot", "e_a_y", dependent=False, **args)
        
        self.declare_partials("F_star_y_dot", "e_p_x", dependent=False, **args)
        self.declare_partials("F_star_y_dot", "e_p_y", dependent=False, **args)
        self.declare_partials("F_star_y_dot", "e_v_x", dependent=False, **args)
        self.declare_partials("F_star_y_dot", "e_v_y", method="exact", **args)
        self.declare_partials("F_star_y_dot", "e_a_x", dependent=False, **args)
        self.declare_partials("F_star_y_dot", "e_a_y", method="exact", **args)
        
        args = {"rows":arange, "cols":c}
        self.declare_partials("F_star_x", "k_p_r__Controller", method="exact", **args)
        self.declare_partials("F_star_x", "k_d_r__Controller", method="exact", **args)
        self.declare_partials("F_star_x", "Mass__System", dependent=False, **args)
        
        self.declare_partials("F_star_y", "k_p_r__Controller", method="exact", **args)
        self.declare_partials("F_star_y", "k_d_r__Controller", method="exact", **args)
        self.declare_partials("F_star_y", "Mass__System", val=g, **args)
        
        self.declare_partials("F_star_x_dot", "k_p_r__Controller", method="exact", **args)
        self.declare_partials("F_star_x_dot", "k_d_r__Controller", method="exact", **args)
        self.declare_partials("F_star_x_dot", "Mass__System", dependent=False, **args)
        
        self.declare_partials("F_star_y_dot", "k_p_r__Controller", method="exact", **args)
        self.declare_partials("F_star_y_dot", "k_d_r__Controller", method="exact", **args)
        self.declare_partials("F_star_y_dot", "Mass__System", dependent=False, **args)
        
    def compute(self,inputs,outputs):
        I = inputs
        O = outputs
        
        O["F_star_x"]= -I["k_p_r__Controller"]*I["e_p_x"]-I["k_d_r__Controller"]*I["e_v_x"]
        O["F_star_y"]= -I["k_p_r__Controller"]*I["e_p_y"]-I["k_d_r__Controller"]*I["e_v_y"]+ I["Mass__System"]*g
        
        O["F_star_x_dot"]= -I["k_p_r__Controller"]*I["e_v_x"]-I["k_d_r__Controller"]*I["e_a_x"]
        O["F_star_y_dot"]= -I["k_p_r__Controller"]*I["e_v_y"]-I["k_d_r__Controller"]*I["e_a_y"]
        
    def compute_partials(self, inputs, partials):
        I = inputs
        
        nn = self.options["num_nodes"]
        ones = np.ones((nn,))
        
        partials["F_star_x", "e_p_x"] = -I["k_p_r__Controller"]*ones
        partials["F_star_x", "e_v_x"] = -I["k_d_r__Controller"]*ones
        partials["F_star_y", "e_p_y"] = -I["k_p_r__Controller"]*ones
        partials["F_star_y", "e_v_y"] = -I["k_d_r__Controller"]*ones
        
        partials["F_star_x_dot", "e_v_x"] = -I["k_p_r__Controller"]*ones
        partials["F_star_x_dot", "e_a_x"] = -I["k_d_r__Controller"]*ones
        partials["F_star_y_dot", "e_v_y"] = -I["k_p_r__Controller"]*ones
        partials["F_star_y_dot", "e_a_y"] = -I["k_d_r__Controller"]*ones
        
        partials["F_star_x", "k_p_r__Controller"] = -I["e_p_x"]
        partials["F_star_x", "k_d_r__Controller"] = -I["e_v_x"]
        partials["F_star_y", "k_p_r__Controller"] = -I["e_p_y"]
        partials["F_star_y", "k_d_r__Controller"] = -I["e_v_y"]
        
        partials["F_star_x_dot", "k_p_r__Controller"] = -I["e_v_x"]
        partials["F_star_x_dot", "k_d_r__Controller"] = -I["e_a_x"]
        partials["F_star_y_dot", "k_p_r__Controller"] = -I["e_v_y"]
        partials["F_star_y_dot", "k_d_r__Controller"] = -I["e_a_y"]
        
class calcDesiredThrust(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
    
    def setup(self):
        nn = self.options["num_nodes"]
        
        for i in ["F_star_x", "F_star_y", "theta"]:
            self.add_input(i, shape=(nn,))
            
        self.add_output("T_star", shape=(nn,), val=10)
        
        arange = np.arange(self.options['num_nodes'])
        args = {"rows":arange, "cols":arange}
        self.declare_partials("T_star", "F_star_x", method='exact', **args)
        self.declare_partials("T_star", "F_star_y", method='exact', **args)
        self.declare_partials("T_star", "theta", method='exact', **args)
        
    def compute(self, inputs, outputs):
        I = inputs
        O = outputs
        # Calculate Thrust and Torque Terms
        O["T_star"] = I["F_star_x"]*(-np.sin(I["theta"])) + I["F_star_y"]*np.cos(I["theta"])
        
    def compute_partials(self, inputs, partials):
        I = inputs
        
        partials["T_star", "F_star_x"] = -np.sin(I["theta"])
        partials["T_star", "F_star_y"] = np.cos(I["theta"])
        partials["T_star", "theta"] = I["F_star_x"]*(-np.cos(I["theta"])) + I["F_star_y"]*(-np.sin(I["theta"]))
        
class calcDesiredTorque(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        shared_kwargs = {"num_nodes": nn}
        
        self.add_subsystem("calcThetaStar", calcThetaStar(**shared_kwargs), promotes=["*"])
        
        e_theta = om.AddSubtractComp("e_theta", ["theta", "theta_star"], vec_size=nn, scaling_factors=[1, -1])
        self.add_subsystem("e_theta", e_theta, promotes=["*"])
        
        e_theta_dot = om.AddSubtractComp("e_theta_dot", ["omega", "theta_star_dot"], vec_size=nn, scaling_factors=[1, -1])
        self.add_subsystem("e_theta_dot", e_theta_dot, promotes=["*"])
        
        self.add_subsystem("calcTauZStar", calcTauZStar(**shared_kwargs), promotes=["*"])
        

class calcThetaStar(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        for i in ["F_star_x", "F_star_y", "F_star_x_dot", "F_star_y_dot"]:
            self.add_input(i, shape=(nn,))
        
        self.add_output("theta_star", shape=(nn,))
        self.add_output("theta_star_dot", shape=(nn,))
        
        arange = np.arange(self.options['num_nodes'])
        args = {"rows":arange, "cols":arange}
        self.declare_partials("theta_star", "F_star_x", method='exact', **args)
        self.declare_partials("theta_star", "F_star_y", method="exact", **args)
        self.declare_partials("theta_star", "F_star_x_dot", dependent=False, **args)
        self.declare_partials("theta_star", "F_star_y_dot", dependent=False, **args)
        
        self.declare_partials("theta_star_dot", "F_star_x", method='exact', **args)
        self.declare_partials("theta_star_dot", "F_star_y", method="exact", **args)
        self.declare_partials("theta_star_dot", "F_star_x_dot", method="exact", **args)
        self.declare_partials("theta_star_dot", "F_star_y_dot", method="exact", **args)
        
    def compute(self, inputs, outputs):
        I = inputs
        O = outputs
        
        Fsx = I["F_star_x"]
        Fsy = I["F_star_y"]
        Fsxd = I["F_star_x_dot"]
        Fsyd = I["F_star_y_dot"]
        
        O["theta_star"]= np.arctan2(Fsy, Fsx) - np.pi/2
        O["theta_star_dot"] = (-Fsy*Fsxd + Fsx*Fsyd)/(Fsx**2 + Fsy**2)
        
    def compute_partials(self, inputs, partials):
        I = inputs
        y = I["F_star_y"]
        x = I["F_star_x"]
        xd = I["F_star_x_dot"]
        yd = I["F_star_y_dot"]
        sumsq = (x**2 + y**2)
        
        partials["theta_star", "F_star_x"] = -y/sumsq
        partials["theta_star", "F_star_y"] = x/sumsq
        
        partials["theta_star_dot", "F_star_x"] = (2*x*xd*y - (x**2)*yd+(y**2)*yd)/(sumsq**2)
        partials["theta_star_dot", "F_star_y"] = (-(x**2)*xd + xd*(y**2) - 2*x*y*yd)/(sumsq**2)
        partials["theta_star_dot", "F_star_x_dot"] = -y/sumsq
        partials["theta_star_dot", "F_star_y_dot"] = x/sumsq
        
    
class calcTauZStar(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_input("k_p_theta__Controller", shape=(1,), tags=['dymos.static_target'])
        self.add_input("k_d_theta__Controller", shape=(1,), tags=['dymos.static_target'])
        
        self.add_input("e_theta", shape=(nn,))
        self.add_input("e_theta_dot", shape=(nn,))
        
        self.add_output("tau_z_star", shape=(nn,))
    
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])

        self.declare_partials("tau_z_star", "k_p_theta__Controller", method="exact", rows=arange, cols=c)
        self.declare_partials("tau_z_star", "k_d_theta__Controller", method="exact", rows=arange, cols=c)
        
        self.declare_partials("tau_z_star", "e_theta", method='exact', rows=arange, cols=arange)
        self.declare_partials("tau_z_star", "e_theta_dot", method='exact', rows=arange, cols=arange)
    
    def compute(self, inputs, outputs):
        I = inputs
        O = outputs
        
        O["tau_z_star"] = -I["k_p_theta__Controller"]*I["e_theta"] - I["k_d_theta__Controller"]*I["e_theta_dot"]
        
    def compute_partials(self, inputs, partials):
        I = inputs
        
        nn = self.options["num_nodes"]
        ones = np.ones((nn,))
        
        partials["tau_z_star", "k_p_theta__Controller"] = -I["e_theta"]
        partials["tau_z_star", "k_d_theta__Controller"] = -I["e_theta_dot"]
        
        partials["tau_z_star", "e_theta"] = -I["k_p_theta__Controller"]*ones
        partials["tau_z_star", "e_theta_dot"] = -I["k_d_theta__Controller"]*ones

class calcDesiredRotorSpeeds(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_input("T_star", shape=(nn,), val=10)
        self.add_input("tau_z_star", shape=(nn,), val=1)
        self.add_input('r__Frame', shape = (1,), units="m", tags=['dymos.static_target'])
        self.add_input('K_T__Propeller', shape=(1,), tags=['dymos.static_target'])
        
        for o in ["omega_1_star", "omega_2_star"]:
            self.add_output(o, shape=(nn,))
            
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])
        
        kwargs = {"rows":arange, "cols":arange}
        self.declare_partials("omega_1_star", "T_star", **kwargs)
        self.declare_partials("omega_1_star", "tau_z_star", **kwargs)
        self.declare_partials("omega_2_star", "T_star", **kwargs)
        self.declare_partials("omega_2_star", "tau_z_star", **kwargs)
        
        kwargs = {"rows":arange, "cols":c}
        self.declare_partials("omega_1_star", "r__Frame", **kwargs)
        self.declare_partials("omega_1_star", "K_T__Propeller", **kwargs)
        self.declare_partials("omega_2_star", "r__Frame", **kwargs)
        self.declare_partials("omega_2_star", "K_T__Propeller", **kwargs)
            
    def compute(self, inputs, outputs):
        I = inputs
        O = outputs
        
        # Calculate Desired Rotor Speed Terms
        omega_1_star_sq = I["T_star"]/(2*I["K_T__Propeller"]) + I["tau_z_star"]/(2*I["K_T__Propeller"]*I["r__Frame"])
        omega_2_star_sq = I["T_star"]/(2*I["K_T__Propeller"]) - I["tau_z_star"]/(2*I["K_T__Propeller"]*I["r__Frame"])
        
        O["omega_1_star"]= np.sign(omega_1_star_sq)*np.sqrt(np.abs(omega_1_star_sq))
        O["omega_2_star"] = np.sign(omega_2_star_sq)*np.sqrt(np.abs(omega_2_star_sq))
    
    def compute_partials(self, inputs, partials):
        I = inputs
        nn = self.options["num_nodes"]
        ones = np.ones((nn,))
        
        def d_f_omegasq(omegasq):
            # Calculates partial derivative of omega_star w.r.t omega_star_sq
            return 1/(2*np.sqrt(np.abs(omegasq)))
        
        omega_1_star_sq = I["T_star"]/(2*I["K_T__Propeller"]) + I["tau_z_star"]/(2*I["K_T__Propeller"]*I["r__Frame"])
        d_f_omegasq_1 = d_f_omegasq(omega_1_star_sq)
        partials["omega_1_star", "T_star"] = d_f_omegasq_1*(1/(2*I["K_T__Propeller"]))
        partials["omega_1_star", "tau_z_star"] = d_f_omegasq_1*(1/(2*I["K_T__Propeller"]*I["r__Frame"]))
        partials["omega_1_star", "K_T__Propeller"] = d_f_omegasq_1*(-I["T_star"]/(2*I["K_T__Propeller"]**2)-I["tau_z_star"]/(2*(I["K_T__Propeller"]**2)*I["r__Frame"]) )
        partials["omega_1_star", "r__Frame"] = d_f_omegasq_1*(-I["tau_z_star"]/(2*I["K_T__Propeller"]*I["r__Frame"]**2))

        omega_2_star_sq = I["T_star"]/(2*I["K_T__Propeller"]) - I["tau_z_star"]/(2*I["K_T__Propeller"]*I["r__Frame"])
        d_f_omegasq_2 = d_f_omegasq(omega_2_star_sq)
        partials["omega_2_star", "T_star"] = d_f_omegasq_2*(1/(2*I["K_T__Propeller"]))
        partials["omega_2_star", "tau_z_star"] = d_f_omegasq_2*(-1/(2*I["K_T__Propeller"]*I["r__Frame"]))
        partials["omega_2_star", "K_T__Propeller"] = d_f_omegasq_2*(-I["T_star"]/(2*I["K_T__Propeller"]**2)+I["tau_z_star"]/(2*(I["K_T__Propeller"]**2)*I["r__Frame"]) )
        partials["omega_2_star", "r__Frame"] = d_f_omegasq_2*(I["tau_z_star"]/(2*I["K_T__Propeller"]*I["r__Frame"]**2))
        
        pass
    
class PlanarPTController(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('saturate', types=bool, default=True)
        self.options.declare('saturation_constant', types=int, default=2)
        self.options.declare('saturation_type', types=str, default="SMOOTH")
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        ### Controller Parameters (Static)
        self.add_input("k_p_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_i_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Integral Gain", tags=['dymos.static_target'])
        self.add_input("k_b_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Anti-Windup Gain", tags=['dymos.static_target'])
        
        ### Dynamic Inputs
        self.add_input("omega_1_star", val=0, shape=(nn,), desc="Right rotor velocity")
        self.add_input("omega_2_star", val=0, shape=(nn,), desc="Left rotor velocity")
        
        self.add_input("omega_1", val=0, shape=(nn,), desc="Right rotor velocity")
        self.add_input("omega_2", val=0, shape=(nn,), desc="Left rotor velocity")

        ### Dynamic Outputs
        self.add_output("u_1", shape=(nn,), val=0, desc="Inverter 1 Input")
        self.add_output("u_2", shape=(nn,), val=0, desc="Inverter 2 Input")

        # Controller States        
        self.add_output("e_omega_1", shape=(nn,), desc="Rotor speed 1 error")
        self.add_output("e_omega_2", shape=(nn,), desc="Rotor speed 2 error")
        
        self.add_output("e_omega_1_I_dot", shape=(nn,), desc="Rotor speed 1 error integral derivative")
        self.add_output("e_omega_2_I_dot", shape=(nn,), desc="Rotor speed 2 error integral derivative")
        
        self.add_input("e_omega_1_I", val=0, shape=(nn,), desc="Rotor speed 1 error integral")
        self.add_input("e_omega_2_I", val=0, shape=(nn,), desc="Rotor speed 2 error integral")
        
        ### Declare Partials
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])
        
        # Use self._var_rel2meta (or self._static_var_rel2meta) dictionary to get all inputs and outputs; check shape field to differentiate inputs from outputs
        partial_method = 'exact'
        input_names = ['k_p_omega__Controller', 'k_i_omega__Controller', 'k_b_omega__Controller', 'omega_1_star', 'omega_2_star', 'omega_1', 'omega_2', 'e_omega_1_I', 'e_omega_2_I']
        output_names = ['u_1', 'u_2', 'e_omega_1', 'e_omega_2', "e_omega_1_I_dot", "e_omega_2_I_dot"]
        for output_name in output_names:
            output_meta = self._var_rel2meta[output_name]
            for input_name in input_names:
                input_meta = self._var_rel2meta[input_name]
                
                if output_meta["shape"] == (1,) and input_meta["shape"] == (1,):
                    self.declare_partials(output_name, input_name, method=partial_method)
                elif output_meta["shape"] == (nn,) and input_meta["shape"] == (1,): 
                    self.declare_partials(output_name, input_name, method=partial_method, rows=arange, cols=c)
                elif output_meta["shape"] == (1,) and input_meta["shape"] == (nn,):
                    self.declare_partials(output_name, input_name, method=partial_method, rows=c, cols=arange)
                elif output_meta["shape"] == (nn,) and input_meta["shape"] == (nn,):
                    self.declare_partials(output_name, input_name, method=partial_method, rows=arange, cols=arange)
                else:
                    raise Exception(f"Partial of {output_name} w.r.t. {input_name} not declared")

    def compute(self, inputs, outputs):
        I = inputs
        O = outputs
        
        def S(u):
            if self.options["saturate"]:
                if self.options["saturation_type"] == "SMOOTH":
                    a = self.options["saturation_constant"]
                    #S = (u/(1 + (u)**a)**(1/a)) # Saturation between -1 and 1
                    S = (1/2)*((2*u-1)*((2*u-1)**a + 1)**(-1/a) + 1) # Saturation between 0 and 1
                elif self.options["saturation_type"] == "EXPLICIT":
                    S = np.clip(u, 0, 1)
                else:
                    raise Exception("Invalid saturation type")
            else:
                S = u
            return S
        
        # Calculate Rotor Speed Errors
        e_omega_1 = I["omega_1"] - I["omega_1_star"]
        e_omega_2 = I["omega_2"] - I["omega_2_star"]
        
        O["e_omega_1"] = e_omega_1
        O["e_omega_2"] = e_omega_2
        
        u_1 = -I["k_p_omega__Controller"]*e_omega_1 - I["k_i_omega__Controller"]*I["e_omega_1_I"]
        u_2 = -I["k_p_omega__Controller"]*e_omega_2 - I["k_i_omega__Controller"]*I["e_omega_2_I"]
        
        u_1_clip = S(u_1)
        u_2_clip = S(u_2)
        
        O["e_omega_1_I_dot"]= e_omega_1 + I["k_b_omega__Controller"]*(u_1 - u_1_clip)
        O["e_omega_2_I_dot"] = e_omega_2 + I["k_b_omega__Controller"]*(u_2 - u_2_clip)
        
        O["u_1"] = u_1_clip #np.clip(u_1, a_min=0, a_max=1)
        O["u_2"] = u_2_clip #np.clip(u_2, a_min=0, a_max=1)

    
    def compute_partials(self, inputs, partials):
        # Inputs: 
        I = inputs
        
        def S(u):
            if self.options["saturate"]:
                if self.options["saturation_type"] == "SMOOTH":
                    a = self.options["saturation_constant"]
                    #S = (u/(1 + (u)**a)**(1/a)) # Saturation between -1 and 1
                    S = (1/2)*((2*u-1)*((2*u-1)**a + 1)**(-1/a) + 1) # Saturation between 0 and 1
                elif self.options["saturation_type"] == "EXPLICIT":
                    S = np.clip(u, 0, 1)
                else:
                    raise Exception("Invalid saturation type")
            else:
                S = u
            return S
        
        def S_prime(u):
            if self.options["saturate"]:
                if self.options["saturation_type"] == "SMOOTH":
                    a = self.options["saturation_constant"]
                    # S_prime = (1+u**a)**(-(1+a)/a) # Saturation between -1 and 1
                    S_prime = ((2*u - 1)**a + 1)**(-(a+1)/a) # Saturation between 0 and 1
                elif self.options["saturation_type"] == "EXPLICIT":
                    S_prime = np.ones(np.shape(u))
                    S_prime[S_prime <= 0] = 0
                    S_prime[S_prime >= 1] = 0
                else:
                    raise Exception("Invalid saturation type")
            else:
                S_prime = 1
            return S_prime
        
        nn = self.options["num_nodes"]
        zeros = np.zeros((nn,))
        ones = np.ones((nn,))
        
        e_omega_1 = I["omega_1"] - I["omega_1_star"]
        e_omega_2 = I["omega_2"] - I["omega_2_star"]
        u_1 = -I["k_p_omega__Controller"]*e_omega_1 - I["k_i_omega__Controller"]*I["e_omega_1_I"]
        u_2 = -I["k_p_omega__Controller"]*e_omega_2 - I["k_i_omega__Controller"]*I["e_omega_2_I"]
        u_1_clip = S(u_1)
        u_2_clip = S(u_2)
        
        partials["e_omega_1", "k_p_omega__Controller"] = zeros
        partials["e_omega_1", "k_i_omega__Controller"] = zeros
        partials["e_omega_1", "k_b_omega__Controller"] = zeros
        partials["e_omega_1", "omega_1_star"] = -1*ones
        partials["e_omega_1", "omega_2_star"] = zeros
        partials["e_omega_1", "omega_1"] = ones
        partials["e_omega_1", "omega_2"] = zeros
        partials["e_omega_1", "e_omega_1_I"] = zeros
        partials["e_omega_1", "e_omega_2_I"] = zeros
        
        partials["e_omega_2", "k_p_omega__Controller"] = zeros
        partials["e_omega_2", "k_i_omega__Controller"] = zeros
        partials["e_omega_2", "k_b_omega__Controller"] = zeros
        partials["e_omega_2", "omega_1_star"] = zeros
        partials["e_omega_2", "omega_2_star"] = -1*ones
        partials["e_omega_2", "omega_1"] = zeros
        partials["e_omega_2", "omega_2"] = ones
        partials["e_omega_2", "e_omega_1_I"] = zeros
        partials["e_omega_2", "e_omega_2_I"] = zeros
        
        S_p_u_1 = S_prime(u_1)
        partials["u_1", "k_p_omega__Controller"] = S_p_u_1*(-e_omega_1)
        partials["u_1", "k_i_omega__Controller"] = S_p_u_1*(-I["e_omega_1_I"])
        partials["u_1", "k_b_omega__Controller"] = S_p_u_1*zeros
        partials["u_1", "omega_1_star"] =  S_p_u_1*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["u_1", "omega_2_star"] =  S_p_u_1*zeros
        partials["u_1", "omega_1"] =  S_p_u_1*(-I["k_p_omega__Controller"]*(ones))
        partials["u_1", "omega_2"] = S_p_u_1*zeros
        partials["u_1", "e_omega_1_I"] = S_p_u_1*(- I["k_i_omega__Controller"]*(ones))
        partials["u_1", "e_omega_2_I"] = S_p_u_1*zeros
        
        S_p_u_2 = S_prime(u_2) 
        partials["u_2", "k_p_omega__Controller"] = S_p_u_2*(-e_omega_2)
        partials["u_2", "k_i_omega__Controller"] = S_p_u_2*(-I["e_omega_2_I"])
        partials["u_2", "k_b_omega__Controller"] = S_p_u_1*zeros
        partials["u_2", "omega_1_star"] = S_p_u_2*zeros
        partials["u_2", "omega_2_star"] = S_p_u_2*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["u_2", "omega_1"] = S_p_u_2*(zeros)
        partials["u_2", "omega_2"] = S_p_u_2*(-I["k_p_omega__Controller"]*(ones))
        partials["u_2", "e_omega_1_I"] = S_p_u_2*zeros
        partials["u_2", "e_omega_2_I"] = S_p_u_2*(- I["k_i_omega__Controller"]*(ones))
        
        partials["e_omega_1_I_dot", "k_p_omega__Controller"] = I["k_b_omega__Controller"]*(-e_omega_1)*(1-S_p_u_1)
        partials["e_omega_1_I_dot", "k_i_omega__Controller"] = I["k_b_omega__Controller"]*(1-S_p_u_1)*(-I["e_omega_1_I"])
        partials["e_omega_1_I_dot", "k_b_omega__Controller"] = (u_1 - u_1_clip)
        partials["e_omega_1_I_dot", "omega_1_star"] = -1*ones + I["k_b_omega__Controller"]*(1-S_p_u_1)*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["e_omega_1_I_dot", "omega_2_star"] = zeros
        partials["e_omega_1_I_dot", "omega_1"] = ones + I["k_b_omega__Controller"]*(1-S_p_u_1)*(-I["k_p_omega__Controller"]*(ones))
        partials["e_omega_1_I_dot", "omega_2"] = zeros
        partials["e_omega_1_I_dot", "e_omega_1_I"] = I["k_b_omega__Controller"]*(1-S_p_u_1)*(- I["k_i_omega__Controller"]*(ones))
        partials["e_omega_1_I_dot", "e_omega_2_I"] = zeros
        
        partials["e_omega_2_I_dot", "k_p_omega__Controller"] = I["k_b_omega__Controller"]*(-e_omega_2)*(1-S_p_u_2)
        partials["e_omega_2_I_dot", "k_i_omega__Controller"] = I["k_b_omega__Controller"]*(1-S_p_u_2)*(-I["e_omega_2_I"])
        partials["e_omega_2_I_dot", "k_b_omega__Controller"] = (u_2 - u_2_clip)
        partials["e_omega_2_I_dot", "omega_1_star"] = zeros
        partials["e_omega_2_I_dot", "omega_2_star"] = -1*ones + I["k_b_omega__Controller"]*(1-S_p_u_2)*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["e_omega_2_I_dot", "omega_1"] = zeros
        partials["e_omega_2_I_dot", "omega_2"] = ones + I["k_b_omega__Controller"]*(1-S_p_u_2)*(-I["k_p_omega__Controller"]*(ones))
        partials["e_omega_2_I_dot", "e_omega_1_I"] = zeros
        partials["e_omega_2_I_dot", "e_omega_2_I"] = I["k_b_omega__Controller"]*(1-S_p_u_2)*(- I["k_i_omega__Controller"]*(ones))
        pass

class calcTrackingError(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('W_x', types=float, default=1.0)
        self.options.declare('W_y', types=float, default=1.0)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_input("e_p_x", shape=(nn,))
        self.add_input("e_p_y", shape=(nn,))
        
        self.add_output("e_T", shape=(nn,))
        
        arange = np.arange(self.options['num_nodes'])
        self.declare_partials("e_T", "e_p_x", method='exact', rows=arange, cols=arange)
        self.declare_partials("e_T", "e_p_y", method='exact', rows=arange, cols=arange)
        
    def compute(self, inputs, outputs):
        e_x = inputs["e_p_x"]
        e_y = inputs["e_p_y"]
        W_x = self.options["W_x"]
        W_y = self.options["W_y"]
        
        outputs["e_T"] = (W_x*e_x**2 + W_y*e_y**2)
        
    def compute_partials(self, inputs, partials):
        e_x = inputs["e_p_x"]
        e_y = inputs["e_p_y"]
        W_x = self.options["W_x"]
        W_y = self.options["W_y"]
        
        partials["e_T", "e_p_x"] = 2*W_x*e_x
        partials["e_T", "e_p_y"] = 2*W_y*e_y
        
        
def genRenameFunctions(openmdao_path):
    def V2T(var):
        # If path to OpenMDAO Variable is specified, Convert it to target openmdao path
        if openmdao_path:
            target = openmdao_path + "." + var
        else:
            target = var
        return target
    
    def V2N(var):
        # If path to OpenMDAO Variable is specified, prepend it to the variable name
        if openmdao_path:
            name = openmdao_path + "_" + var
        else:
            name = var
        return name
    
    return(V2T, V2N)
        
def ModifyPhase(phase, openmdao_path="", body_model_path="", powertrain_path=""):
    (V2T, V2N) = genRenameFunctions(openmdao_path)
    (V2T_BM, V2N_BM) = genRenameFunctions(body_model_path)
    (V2T_PT, V2N_PT) = genRenameFunctions(powertrain_path)
    
    # Add BM and PT States to Targets
    
    bm_pairs = [("x","x"), ("y","y"), ("theta","theta"), ("omega", "omega"), ("v_x","v_x"), ("v_y","v_y")]
    for bm_name,c_name in bm_pairs:
        trgt = phase.state_options[V2N_BM(bm_name)]['targets']
        if trgt is _unspecified:
            trgt_mod = [V2T(c_name)]
        else:
            trgt_mod = [*trgt, V2T(c_name)]
        phase.state_options[V2N_BM(bm_name)]['targets'] = trgt_mod
        
    pt_pairs = [("x2","omega_1"), ("x3","omega_2")]
    for pt_name,c_name in pt_pairs:
        trgt = phase.state_options[V2N_PT(pt_name)]['targets']
        if trgt is _unspecified:
            trgt_mod = [V2T(c_name)]
        else:
            trgt_mod = [*trgt, V2T(c_name)]
        phase.state_options[V2N_PT(pt_name)]['targets'] = trgt_mod
        
    # Add Reference Trajectory Input
    for i in ["x_T", "y_T", "v_x_T", "v_y_T", 'a_x_T', "a_y_T"]:
        phase.add_control(V2N(i), targets=V2T(i), opt=False)
    
    # Add Controller States
    phase.add_state(V2N("e_omega_1_I"), rate_source=V2T("e_omega_1_I_dot"), targets=[V2T("e_omega_1_I")], units='rad')
    phase.add_state(V2N("e_omega_2_I"), rate_source=V2T("e_omega_2_I_dot"), targets=[V2T("e_omega_2_I")], units='rad')
    
    # Add Tracking Error State
    phase.add_state(V2N("e_T_I"), rate_source=V2T("e_T"), lower=0)
    
    # Add Timeseries Outputs
    # TODO: if this doesn't work, may need to add shape option explicitly
    for out in ["u_1", "u_2", "F_star_x", "F_star_y", "T_star", "theta_star", "tau_z_star", "omega_1_star", "omega_2_star", "e_omega_1", "e_omega_2"]:
        phase.add_timeseries_output(output_name=V2N(out), name=V2T(out))
    
def ModifyTraj(traj, openmdao_path=""):
    (V2T, V2N) = genRenameFunctions(openmdao_path)
    phase_names = traj._phases.keys()
    
    # Add Trajectory Parameters
    opts = {'opt':False,'static_target':True}
    
    controller_params = ["k_p_r__Controller", "k_d_r__Controller", "k_p_theta__Controller", "k_d_theta__Controller", "k_p_omega__Controller", "k_i_omega__Controller", "k_b_omega__Controller"]
    sys_params = ["Mass__System", "r__Frame", "K_T__Propeller"]
    
    for param in controller_params:
        traj.add_parameter(param, targets={p:[V2T(param)] for p in phase_names}, **opts)
        
    for param in sys_params:
        trgt = traj.parameter_options[param]['targets']
        if trgt is _unspecified:
            trgt_mod = {p:[V2T(param)] for p in phase_names}
        else:
            trgt_mod = dict()
            for k,v in trgt.items():
                trgt_mod[k] = [*v, V2T(param)]
        traj.parameter_options[param]['targets'] = trgt_mod
        
if __name__ == "__main__":
        # Run N2 and Model Checks
    import openmdao.api as om
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    os.chdir(os.path.dirname(__file__))
    try:
        os.mkdir('./ModelChecks/')
    except:
        pass
    os.chdir('./ModelChecks/')
    
    def checkModelClass(model_class):
        class_name = model_class.__name__
        
        if not os.path.isdir(class_name):
            os.mkdir(class_name)
        os.chdir(class_name)
        
        print(f"Checking Model Class: {class_name}")
        
        mdl_args = {"num_nodes":10}
        p = om.Problem(model=om.Group())
        p.model.add_subsystem("sys", model_class(**mdl_args))
        p.setup()
        p.final_setup()
        
        # Visualize:
        om.n2(p)
        #om.view_connections(p)
        
        # Checks:
        p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
        p.check_partials(compact_print=True)
        
        os.chdir('..')
    
    checkModelClass(PlanarController)
    
### ARCHIVE ###
# class PlanarController(om.ExplicitComponent):
#     def initialize(self):
#         self.options.declare('num_nodes', types=int)
        
#     def setup(self):
#         nn = self.options["num_nodes"]
        
#         ### Controller Parameters (Static)
#         self.add_input("k_p_r__Controller", shape=(1,), val=1, desc="Position Proportional Gain", tags=['dymos.static_target'])
#         self.add_input("k_d_r__Controller", shape=(1,), val=1, desc="Position Derivative Gain", tags=['dymos.static_target'])
#         self.add_input("k_p_theta__Controller", shape=(1,), val=1, desc="Angle Proportional Gain", tags=['dymos.static_target'])
#         self.add_input("k_p_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Proportional Gain", tags=['dymos.static_target'])
#         self.add_input("k_i_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Integral Gain", tags=['dymos.static_target'])

#         ### Other Parameters (Static)
#         self.add_input('Mass__System', shape = (1,), val=1, desc='mass', units='kg', tags=['dymos.static_target'])
#         self.add_input('r__Frame', shape = (1,), val=0.1, desc='arm length', units='m', tags=['dymos.static_target'])
#         self.add_input('K_T__Propeller', shape=(1,), val=7e-6, desc="Lumped Thrust Coefficient", tags=['dymos.static_target'])
        
#         ### Dynamic Inputs
#         self.add_input("x", val=0, shape=(nn,), desc="x trajectory", units='m')
#         self.add_input("y", val=0, shape=(nn,), desc="y trajectory", units='m')
#         self.add_input("theta", val=0, shape=(nn,), desc="rotation", units='rad')

#         self.add_input("x_T", val=0, shape=(nn,), desc="x reference trajectory", units='m')
#         self.add_input("y_T", val=0, shape=(nn,), desc="y reference trajectory", units='m')

#         self.add_input("x_dot", val=0, shape=(nn,), desc="x velocity", units='m/s')
#         self.add_input("y_dot", val=0, shape=(nn,), desc="y velocity", units='m/s')
                
#         self.add_input("v_x_T", val=0, shape=(nn,), desc="x reference velocity", units='m/s')
#         self.add_input("y_T_dot", val=0, shape=(nn,), desc="y reference velocity", units='m/s')
        
#         self.add_input("omega_1", val=0, shape=(nn,), desc="Right rotor velocity")
#         self.add_input("omega_2", val=0, shape=(nn,), desc="Left rotor velocity")

#         ### Dynamic Outputs
#         self.add_output("u_1", shape=(nn,), desc="Inverter 1 Input")
#         self.add_output("u_2", shape=(nn,), desc="Inverter 2 Input")

#         # Controller States        
#         self.add_output("e_omega_1", shape=(nn,), desc="Rotor speed 1 error")
#         self.add_output("e_omega_2", shape=(nn,), desc="Rotor speed 2 error")
        
#         self.add_output("F_star_x", shape=(nn,), desc="Desired Force Vector x")
#         self.add_output("F_star_y", shape=(nn,), desc="Desired Force Vector y")
#         self.add_output("T_star", shape=(nn,), desc="Desired Thrust")
#         self.add_output("theta_star", shape=(nn,), desc="Desired Angle")
#         self.add_output("tau_z_star", shape=(nn,), desc="Desired Moment")
#         self.add_output("omega_1_star", shape=(nn,), desc="Desired Rotor 1 Speed")
#         self.add_output("omega_2_star", shape=(nn,), desc="Desired Rotor 2 Speed")
        
#         self.add_input("e_omega_1_I", val=0, shape=(nn,), desc="Rotor speed 1 error integral")
#         self.add_input("e_omega_2_I", val=0, shape=(nn,), desc="Rotor speed 2 error integral")
        
#         ### Declare Partials
#         arange = np.arange(self.options['num_nodes'])
#         c = np.zeros(self.options['num_nodes'])
        
#         # Use self._var_rel2meta (or self._static_var_rel2meta) dictionary to get all inputs and outputs; check shape field to differentiate inputs from outputs
#         partial_method = 'cs'
#         for output_name in self._static_var_rel_names["output"]:
#             output_meta = self._static_var_rel2meta[output_name]
#             for input_name in self._static_var_rel_names["input"]:
#                 input_meta = self._static_var_rel2meta[input_name]
                
#                 if output_meta["shape"] == (1,) and input_meta["shape"] == (1,):
#                     self.declare_partials(output_name, input_name, method=partial_method)
#                 elif output_meta["shape"] == (nn,) and input_meta["shape"] == (1,): 
#                     self.declare_partials(output_name, input_name, method=partial_method, rows=arange, cols=c)
#                 elif output_meta["shape"] == (1,) and input_meta["shape"] == (nn,):
#                     self.declare_partials(output_name, input_name, method=partial_method, rows=c, cols=arange)
#                 elif output_meta["shape"] == (nn,) and input_meta["shape"] == (nn,):
#                     self.declare_partials(output_name, input_name, method=partial_method, rows=arange, cols=arange)
#                 else:
#                     raise Exception(f"Partial of {output_name} w.r.t. {input_name} not declared")

#     def compute(self, inputs, outputs):
#         I = inputs
#         O = outputs
        
#         # Define Error Terms
#         e_p_x = I["x"] - I["x_T"]
#         e_p_y = I["y"] - I["y_T"]
        
#         e_v_x = I["x_dot"] - I["v_x_T"]
#         e_v_y = I["y_dot"] - I["y_T_dot"]
        
#         # Calculate Desired Force Vector
#         F_star_x = -I["k_p_r__Controller"]*e_p_x-I["k_d_r__Controller"]*e_v_x
#         F_star_y = -I["k_p_r__Controller"]*e_p_y-I["k_d_r__Controller"]*e_v_y + I["Mass__System"]*g
        
#         # Calculate Thrust and Torque Terms
#         T_star = F_star_x*(-np.sin(I["theta"])) + F_star_y*np.cos(I["theta"])
        
#         theta_star = np.arctan2(F_star_y, F_star_x) - np.pi/2
#         e_theta = I["theta"] - theta_star
#         tau_z_star = -I["k_p_theta__Controller"]*e_theta
        
#         # Calculate Desired Rotor Speed Terms
#         omega_1_star_sq = T_star/(2*I["K_T__Propeller"]) + tau_z_star/(2*I["K_T__Propeller"]*I["r__Frame"])
#         omega_2_star_sq = T_star/(2*I["K_T__Propeller"]) - tau_z_star/(2*I["K_T__Propeller"]*I["r__Frame"])
        
#         omega_1_star = np.sign(omega_1_star_sq)*np.sqrt(np.abs(omega_1_star_sq))
#         omega_2_star = np.sign(omega_2_star_sq)*np.sqrt(np.abs(omega_2_star_sq))
        
#         # Calculate Rotor Speed Errors
#         e_omega_1 = I["omega_1"] - omega_1_star
#         e_omega_2 = I["omega_2"] - omega_2_star
        
#         O["e_omega_1"] = e_omega_1
#         O["e_omega_2"] = e_omega_2
        
#         u_1 = -I["k_p_omega__Controller"]*e_omega_1 - I["k_i_omega__Controller"]*I["e_omega_1_I"]
#         u_2 = -I["k_p_omega__Controller"]*e_omega_2 - I["k_i_omega__Controller"]*I["e_omega_2_I"]
        
#         O["u_1"] = np.clip(u_1, a_min=0, a_max=1)
#         O["u_2"] = np.clip(u_2, a_min=0, a_max=1)
        
#         # Logging
#         O["F_star_x"] = F_star_x
#         O["F_star_y"] = F_star_y
#         O["T_star"] = T_star
#         O["theta_star"] = theta_star
#         O["tau_z_star"] = tau_z_star
#         O["omega_1_star"] = omega_1_star
#         O["omega_2_star"] = omega_2_star

    
#     def compute_partials(self, inputs, partials):
#         #TODO: Implement after controller design has been finalized
#         pass