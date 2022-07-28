# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:57:28 2022

@author: renkert2
"""

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
import logging

g = 9.80665

class PlanarControllerParams(P.ParamSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        kw = {"parent":"Controller", "component":"PlanarController"}
        self.add(P.Param(name="k_p_omega", val=1, desc="Rotor Speed Proportional Gain", strID="k_p_omega__Controller", **kw))
        self.add(P.Param(name="k_i_omega", val=1, desc="Rotor Speed Integral Gain", strID="k_i_omega__Controller", **kw))
        self.add(P.Param(name="k_b_omega", val=1, desc="Rotor Speed Anti-Windup Gain", strID="k_b_omega__Controller", **kw))

class PlanarController(om.ExplicitComponent):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        ### Controller Parameters (Static)
        self.add_input("k_p_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Proportional Gain", tags=['dymos.static_target'])
        self.add_input("k_i_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Integral Gain", tags=['dymos.static_target'])
        self.add_input("k_b_omega__Controller", shape=(1,), val=1, desc="Rotor Speed Anti-Windup Gain", tags=['dymos.static_target'])
        
        ### Dynamic Inputs
        self.add_input("omega_1_des", val=0, shape=(nn,), desc="Right rotor velocity")
        self.add_input("omega_2_des", val=0, shape=(nn,), desc="Left rotor velocity")
        
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
        input_names = ['k_p_omega__Controller', 'k_i_omega__Controller', 'omega_1_des', 'omega_2_des', 'omega_1', 'omega_2', 'e_omega_1_I', 'e_omega_2_I']
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
        S = lambda u: (u/(1 + (u)**10)**(1/10))
        
        # Calculate Rotor Speed Errors
        e_omega_1 = I["omega_1"] - I["omega_1_des"]
        e_omega_2 = I["omega_2"] - I["omega_2_des"]
        
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
        
        #O["u_1"] = np.clip(u_1, a_min=0, a_max=1)
        #O["u_2"] = np.clip(u_2, a_min=0, a_max=1)

    
    def compute_partials(self, inputs, partials):
        # Inputs: 
        I = inputs
        S_prime = lambda u: (1/(1 + (u)**10)**(11/10))
        nn = self.options["num_nodes"]
        zeros = np.zeros((nn,))
        ones = np.ones((nn,))
        
        e_omega_1 = I["omega_1"] - I["omega_1_des"]
        e_omega_2 = I["omega_2"] - I["omega_2_des"]
        u_1 = -I["k_p_omega__Controller"]*e_omega_1 - I["k_i_omega__Controller"]*I["e_omega_1_I"]
        u_2 = -I["k_p_omega__Controller"]*e_omega_2 - I["k_i_omega__Controller"]*I["e_omega_2_I"]
        
        partials["e_omega_1", "k_p_omega__Controller"] = zeros
        partials["e_omega_1", "k_i_omega__Controller"] = zeros
        partials["e_omega_1", "omega_1_des"] = -1*ones
        partials["e_omega_1", "omega_2_des"] = zeros
        partials["e_omega_1", "omega_1"] = ones
        partials["e_omega_1", "omega_2"] = zeros
        partials["e_omega_1", "e_omega_1_I"] = zeros
        partials["e_omega_1", "e_omega_2_I"] = zeros
        
        partials["e_omega_2", "k_p_omega__Controller"] = zeros
        partials["e_omega_2", "k_i_omega__Controller"] = zeros
        partials["e_omega_2", "omega_1_des"] = zeros
        partials["e_omega_2", "omega_2_des"] = -1*ones
        partials["e_omega_2", "omega_1"] = zeros
        partials["e_omega_2", "omega_2"] = ones
        partials["e_omega_2", "e_omega_1_I"] = zeros
        partials["e_omega_2", "e_omega_2_I"] = zeros
        
        S_p_u_1 = S_prime(u_1)
        partials["u_1", "k_p_omega__Controller"] = S_p_u_1*(-e_omega_1)
        partials["u_1", "k_i_omega__Controller"] = S_p_u_1*(-I["e_omega_1_I"])
        partials["u_1", "omega_1_des"] =  S_p_u_1*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["u_1", "omega_2_des"] =  S_p_u_1*zeros
        partials["u_1", "omega_1"] =  S_p_u_1*(-I["k_p_omega__Controller"]*(ones))
        partials["u_1", "omega_2"] = S_p_u_1*zeros
        partials["u_1", "e_omega_1_I"] = S_p_u_1*(- I["k_i_omega__Controller"]*(ones))
        partials["u_1", "e_omega_2_I"] = S_p_u_1*zeros
        
        S_p_u_2 = S_prime(u_2) 
        partials["u_2", "k_p_omega__Controller"] = S_p_u_2*(-e_omega_2)
        partials["u_2", "k_i_omega__Controller"] = S_p_u_2*(-I["e_omega_2_I"])
        partials["u_2", "omega_1_des"] = S_p_u_2*zeros
        partials["u_2", "omega_2_des"] = S_p_u_2*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["u_2", "omega_1"] = S_p_u_2*(zeros)
        partials["u_2", "omega_2"] = S_p_u_2*(-I["k_p_omega__Controller"]*(ones))
        partials["u_2", "e_omega_1_I"] = S_p_u_2*zeros
        partials["u_2", "e_omega_2_I"] = S_p_u_2*(- I["k_i_omega__Controller"]*(ones))
        
        partials["e_omega_1_I_dot", "k_p_omega__Controller"] = I["k_b_omega__Controller"]*(-e_omega_1)*(1-S_p_u_1)
        partials["e_omega_1_I_dot", "k_i_omega__Controller"] = I["k_b_omega__Controller"]*(1-S_p_u_1)*(-I["e_omega_1_I"])
        partials["e_omega_1_I_dot", "omega_1_des"] = -1*ones + I["k_b_omega__Controller"]*(1-S_p_u_1)*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["e_omega_1_I_dot", "omega_2_des"] = zeros
        partials["e_omega_1_I_dot", "omega_1"] = ones + I["k_b_omega__Controller"]*(1-S_p_u_1)*(-I["k_p_omega__Controller"]*(ones))
        partials["e_omega_1_I_dot", "omega_2"] = zeros
        partials["e_omega_1_I_dot", "e_omega_1_I"] = I["k_b_omega__Controller"]*(1-S_p_u_1)*(- I["k_i_omega__Controller"]*(ones))
        partials["e_omega_1_I_dot", "e_omega_2_I"] = zeros
        
        partials["e_omega_2_I_dot", "k_p_omega__Controller"] = I["k_b_omega__Controller"]*(-e_omega_2)*(1-S_p_u_2)
        partials["e_omega_2_I_dot", "k_i_omega__Controller"] = I["k_b_omega__Controller"]*(1-S_p_u_2)*(-I["e_omega_2_I"])
        partials["e_omega_2_I_dot", "omega_1_des"] = zeros
        partials["e_omega_2_I_dot", "omega_2_des"] = -1*ones + I["k_b_omega__Controller"]*(1-S_p_u_2)*(-I["k_p_omega__Controller"]*(-1*ones))
        partials["e_omega_2_I_dot", "omega_1"] = zeros
        partials["e_omega_2_I_dot", "omega_2"] = ones + I["k_b_omega__Controller"]*(1-S_p_u_2)*(-I["k_p_omega__Controller"]*(ones))
        partials["e_omega_2_I_dot", "e_omega_1_I"] = zeros
        partials["e_omega_2_I_dot", "e_omega_2_I"] = I["k_b_omega__Controller"]*(1-S_p_u_2)*(- I["k_i_omega__Controller"]*(ones))
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
        
def ModifyPhase(phase, openmdao_path="", powertrain_path=""):
    (V2T, V2N) = genRenameFunctions(openmdao_path)
    (V2T_PT, V2N_PT) = genRenameFunctions(powertrain_path)
    
    # Add BM and PT States to Targets
    pt_pairs = [("x2","omega_1"), ("x3","omega_2")]
    for pt_name,c_name in pt_pairs:
        trgt = phase.state_options[V2N_PT(pt_name)]['targets']
        if trgt is _unspecified:
            trgt_mod = [V2T(c_name)]
        else:
            trgt_mod = [*trgt, V2T(c_name)]
        phase.state_options[V2N_PT(pt_name)]['targets'] = trgt_mod
        
    # Add Reference Trajectory Input
    for i in ["omega_1_des", "omega_2_des"]:
        phase.add_control(V2N(i), targets=V2T(i), opt=False)
    
    # Add Controller States
    phase.add_state(V2N("e_omega_1_I"), rate_source=V2T("e_omega_1_I_dot"), targets=[V2T("e_omega_1_I")], units='rad')
    phase.add_state(V2N("e_omega_2_I"), rate_source=V2T("e_omega_2_I_dot"), targets=[V2T("e_omega_2_I")], units='rad')
    
    # Add Timeseries Outputs
    # TODO: if this doesn't work, may need to add shape option explicitly
    for out in ["u_1", "u_2", "e_omega_1", "e_omega_2"]:
        phase.add_timeseries_output(output_name=V2N(out), name=V2T(out))
    
def ModifyTraj(traj, openmdao_path=""):
    (V2T, V2N) = genRenameFunctions(openmdao_path)
    phase_names = traj._phases.keys()
    
    # Add Trajectory Parameters
    opts = {'opt':False,'static_target':True}
    
    controller_params = ["k_p_omega__Controller", "k_i_omega__Controller", "k_b_omega__Controller"]
    
    for param in controller_params:
        traj.add_parameter(param, targets={p:[V2T(param)] for p in phase_names}, **opts)
        
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