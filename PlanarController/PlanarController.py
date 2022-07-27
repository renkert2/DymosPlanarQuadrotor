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
import DynamicModel as DM
import Param as P

g = 9.80665

class PlanarControllerParams(P.ParamSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        kw = {"parent":"Controller", "component":"PlanarController"}
        self.add(P.Param(name="k_p_r", val=1, desc="Position Proportional Gain", strID="k_p_r__Controller", **kw))
        self.add(P.Param(name="k_d_r", val=1, desc="Position Derivative Gain", strID="k_d_r__Controller", **kw))
        self.add(P.Param(name="k_p_theta", val=1, desc="Angle Proportional Gain", strID="k_p_theta__Controller", **kw))
        self.add(P.Param(name="k_p_omega", val=1, desc="Rotor Speed Proportional Gain", strID="k_p_omega__Controller", **kw))
        self.add(P.Param(name="k_i_omega", val=1, desc="Rotor Speed Integral Gain", strID="k_i_omega__Controller", **kw))

class PlanarController(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        ### Controller Parameters (Static)
        self.add_input("k_p_r__Controller", shape=(1,), val=1, desc="Position Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_d_r__Controller", shape=(1,), val=1, desc="Position Derivative Gain", tags=['dymos.static_target'])
        self.add_input("k_p_theta__Controller", shape=(1,), val=1, desc="Angle Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_p_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_i_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Integral Gain", tags=['dymos.static_target'])

        ### Other Parameters (Static)
        self.add_input('Mass__System', shape = (1,), val=1, desc='mass', units='kg', tags=['dymos.static_target'])
        self.add_input('r__Frame', shape = (1,), val=0.1, desc='arm length', units='m', tags=['dymos.static_target'])
        self.add_input('K_T__Propeller', shape=(1,), val=7e-6, desc="Lumped Thrust Coefficient", tags=['dymos.static_target'])
        
        ### Dynamic Inputs
        self.add_input("x", val=0, shape=(nn,), desc="x trajectory", units='m')
        self.add_input("y", val=0, shape=(nn,), desc="y trajectory", units='m')
        self.add_input("theta", val=0, shape=(nn,), desc="rotation", units='rad')

        self.add_input("x_T", val=0, shape=(nn,), desc="x reference trajectory", units='m')
        self.add_input("y_T", val=0, shape=(nn,), desc="y reference trajectory", units='m')

        self.add_input("x_dot", val=0, shape=(nn,), desc="x velocity", units='m/s')
        self.add_input("y_dot", val=0, shape=(nn,), desc="y velocity", units='m/s')
                
        self.add_input("x_T_dot", val=0, shape=(nn,), desc="x reference velocity", units='m/s')
        self.add_input("y_T_dot", val=0, shape=(nn,), desc="y reference velocity", units='m/s')
        
        self.add_input("omega_1", val=0, shape=(nn,), desc="Right rotor velocity")
        self.add_input("omega_2", val=0, shape=(nn,), desc="Left rotor velocity")

        ### Dynamic Outputs
        self.add_output("u_1", shape=(nn,), desc="Inverter 1 Input")
        self.add_output("u_2", shape=(nn,), desc="Inverter 2 Input")

        # Controller States        
        self.add_output("e_omega_1", shape=(nn,), desc="Rotor speed 1 error")
        self.add_output("e_omega_2", shape=(nn,), desc="Rotor speed 2 error")
        
        self.add_output("F_star_x", shape=(nn,), desc="Desired Force Vector x")
        self.add_output("F_star_y", shape=(nn,), desc="Desired Force Vector y")
        self.add_output("T_star", shape=(nn,), desc="Desired Thrust")
        self.add_output("theta_star", shape=(nn,), desc="Desired Angle")
        self.add_output("tau_z_star", shape=(nn,), desc="Desired Moment")
        self.add_output("omega_1_star", shape=(nn,), desc="Desired Rotor 1 Speed")
        self.add_output("omega_2_star", shape=(nn,), desc="Desired Rotor 2 Speed")
        
        self.add_input("e_omega_1_I", val=0, shape=(nn,), desc="Rotor speed 1 error integral")
        self.add_input("e_omega_2_I", val=0, shape=(nn,), desc="Rotor speed 2 error integral")
        
        ### Declare Partials
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])
        
        # Use self._var_rel2meta (or self._static_var_rel2meta) dictionary to get all inputs and outputs; check shape field to differentiate inputs from outputs
        partial_method = 'cs'
        for output_name in self._static_var_rel_names["output"]:
            output_meta = self._static_var_rel2meta[output_name]
            for input_name in self._static_var_rel_names["input"]:
                input_meta = self._static_var_rel2meta[input_name]
                
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
        
        # Define Error Terms
        e_p_x = I["x"] - I["x_T"]
        e_p_y = I["y"] - I["y_T"]
        
        e_v_x = I["x_dot"] - I["x_T_dot"]
        e_v_y = I["y_dot"] - I["y_T_dot"]
        
        # Calculate Desired Force Vector
        F_star_x = -I["k_p_r__Controller"]*e_p_x-I["k_d_r__Controller"]*e_v_x
        F_star_y = -I["k_p_r__Controller"]*e_p_y-I["k_d_r__Controller"]*e_v_y + I["Mass__System"]*g
        
        # Calculate Thrust and Torque Terms
        T_star = F_star_x*(-np.sin(I["theta"])) + F_star_y*np.cos(I["theta"])
        
        theta_star = np.arctan2(F_star_y, F_star_x) - np.pi/2
        e_theta = I["theta"] - theta_star
        tau_z_star = -I["k_p_theta__Controller"]*e_theta
        
        # Calculate Desired Rotor Speed Terms
        omega_1_star_sq = T_star/(2*I["K_T__Propeller"]) + tau_z_star/(2*I["K_T__Propeller"]*I["r__Frame"])
        omega_1_star_sq = np.clip(omega_1_star_sq, a_min=0, a_max=None)
            
        omega_2_star_sq = T_star/(2*I["K_T__Propeller"]) - tau_z_star/(2*I["K_T__Propeller"]*I["r__Frame"])
        omega_2_star_sq = np.clip(omega_2_star_sq, a_min=0, a_max=None)
        
        omega_1_star = np.sqrt(omega_1_star_sq)
        omega_2_star = np.sqrt(omega_2_star_sq)
        
        # Calculate Rotor Speed Errors
        e_omega_1 = I["omega_1"] - omega_1_star
        e_omega_2 = I["omega_2"] - omega_2_star
        
        O["e_omega_1"] = e_omega_1
        O["e_omega_2"] = e_omega_2
        
        u_1 = -I["k_p_omega__Controller"]*e_omega_1 - I["k_i_omega__Controller"]*I["e_omega_1_I"]
        u_2 = -I["k_p_omega__Controller"]*e_omega_2 - I["k_i_omega__Controller"]*I["e_omega_2_I"]
        
        O["u_1"] = np.clip(u_1, a_min=0, a_max=1)
        O["u_2"] = np.clip(u_2, a_min=0, a_max=1)
        
        # Logging
        O["F_star_x"] = F_star_x
        O["F_star_y"] = F_star_y
        O["T_star"] = T_star
        O["theta_star"] = theta_star
        O["tau_z_star"] = tau_z_star
        O["omega_1_star"] = omega_1_star
        O["omega_2_star"] = omega_2_star

    
    def compute_partials(self, inputs, partials):
        #TODO: Implement after controller design has been finalized
        pass
    
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
    
    bm_pairs = [("x","x"), ("y","y"), ("theta","theta"),("v_x","x_dot"), ("v_y","y_dot")]
    for bm_name,c_name in bm_pairs:
        trgt = phase.state_options[V2N_BM(bm_name)]['targets']
        if isinstance(trgt, omcore.constants._ReprClass):
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
    for i in ["x_T", "y_T", "x_T_dot", "y_T_dot"]:
        phase.add_control(V2N(i), targets=V2T(i), opt=False)
    
    # Add Controller States
    phase.add_state(V2N("e_omega_1_I"), rate_source=V2T("e_omega_1"), targets=[V2T("e_omega_1_I")], units='rad')
    phase.add_state(V2N("e_omega_2_I"), rate_source=V2T("e_omega_2"), targets=[V2T("e_omega_2_I")], units='rad')
    
    # Add Timeseries Outputs
    # TODO: if this doesn't work, may need to add shape option explicitly
    for out in ["u_1", "u_2", "F_star_x", "F_star_y", "T_star", "theta_star", "tau_z_star", "omega_1_star", "omega_2_star", "e_omega_1", "e_omega_2"]:
        phase.add_timeseries_output(output_name=V2N(out), name=V2T(out))
    
def ModifyTraj(traj, openmdao_path=""):
    (V2T, V2N) = genRenameFunctions(openmdao_path)
    phase_names = traj._phases.keys()
    
    # Add Trajectory Parameters
    opts = {'opt':False,'static_target':True}
    
    controller_params = ["k_p_r__Controller", "k_d_r__Controller", "k_p_theta__Controller", "k_p_omega__Controller", "k_i_omega__Controller"]
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