# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 16:07:54 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import PlanarBody.PlanarQuadrotorODE as bm
import PlanarPT.PlanarPTModels as pt 
import PlanarPT.Surrogates.Surrogates as surrogates
import dymos as dm
import DynamicModel as dmm
import os


class PlanarSystemDynamicModel(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_subsystem(name="PT", subsys=pt.PlanarPTModel(num_nodes=nn))
        self.add_subsystem(name="BM", subsys=bm.PlanarQuadrotorODE(num_nodes=nn))
        
        self.connect("PT.y1", "BM.u_1")
        self.connect("PT.y3", "BM.u_2")
        
class PlanarSystemDynamicPhase(dmm.DynamicPhase):
    def __init__(self, *args, **kwargs):
        # Instantiate a Phase and add it to the Trajectory.
        # Here the transcription is necessary but not particularly relevant.
        super().__init__(ode_class=PlanarSystemDynamicModel, *args, **kwargs)
    
        ## Add PowerTrain Information.  In the PlanarSystemDynamicModel, the PlanarPowerTrainModel dynamic model 
        # is added as a subsystem named PT.  When we specify the open_mdao path as PT, init_vars will find the 
        # relevant metadata and use it to add the states, controls, etc to the phase.  The phase variables name will
        # prepend the variable name with the path.  For example, the "x1" state for model.PT.Z would be 
        # referred to as state "PT_Z_x1"
    
    def init_vars(self):
        super().init_vars(openmdao_path="PT", 
                        state_names=["x"],
                        control_names = ["u","d"],
                        parameter_names = ["theta"],
                        output_names = ["y", "a"],
                        var_opts = {"d":{"val":0}})
        ## Add Body Model Information
        # The PlanarQuadrotorODE Module has a method which takes an existing phase
        # and manually adds its states and controls to it.  
        self = bm.ModifyPhase(self, openmdao_path="BM", declare_controls=False)
    

def makePlanarSystemModel(phase):
    model = om.Group();
    
    # Add Battery surrogate, promote all parameter inputs and outputs to top level.  Everything has unique names at this point so we should be good. 
    bs = surrogates.BatterySurrogate()
    model.add_subsystem('surr_batt', bs, promotes=["*"])
    
    ms = surrogates.MotorSurrogate()
    model.add_subsystem('surr_motor', ms, promotes=["*"])
    
    # Add Mass 
    mass_comp = om.ExecComp("Mass = Mass__Battery + Mass__Motor + 1")
    model.add_subsystem("mass", mass_comp, promotes=['*'])
    
    # Setup trajectory and add phase
    traj = model.add_subsystem('traj', dm.Trajectory())
    traj.add_phase('phase0', phase)

    # Promote PT Parameters
    meta = dmm.ImportMetadata('C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor/PlanarPT/PlanarPowerTrainModel')
    param_table = meta["ParamTable"]
    theta_names = [x["SymID"] for x in param_table]
    for theta in theta_names:
        theta_path = "PT_" + theta
        model.promotes('traj', inputs=[((f'phase0.parameters:%s' % theta_path),theta)])
    
    # Promote BM Parameters
    model.promotes('traj', inputs=[('phase0.parameters:BM_m', 'Mass')])
    
    
        
    return model, traj



if __name__ == "__main__":
    # Run N2 and Model Checks
    import openmdao.api as om
    import os
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    os.chdir(os.path.dirname(__file__))
    try:
        os.mkdir('./ModelChecks/')
    except:
        pass
    os.chdir('./ModelChecks/')
    
    def checkProblem(p):
            p.setup()
            p.final_setup()
        
            # Visualize:
            om.n2(p)
            om.view_connections(p)
            
            # Checks:
            p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
            p.check_partials(compact_print=True)
    
    ## Dynamic Model
    print("Checking PlanarPTModel")
    p = om.Problem(model=PlanarSystemDynamicModel(num_nodes = 10))
    try:
        os.mkdir('./PlanarSystemDynamicModel/')
    except:
        pass
    os.chdir('./PlanarSystemDynamicModel/')
    checkProblem(p)

