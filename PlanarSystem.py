# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 16:07:54 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import PlanarBody.PlanarQuadrotorODE as bm
import PlanarPT.PlanarPTModel as pt 
import PlanarPT.Surrogates.BatterySurrogate as battSurrogate
import DymosModel as dmm
import dymos as dm
import os


class PlanarSystemDynamicModel(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_subsystem(name="PT", subsys=pt.PlanarPTModel(num_nodes=nn))
        self.add_subsystem(name="BM", subsys=bm.PlanarQuadrotorODE(num_nodes=nn))
        
        self.connect("PT.y12", "BM.u_1")
        self.connect("PT.y14", "BM.u_2")

def makePlanarSystemModel(phase):
    model = om.Group();
    
    # Add Battery surrogate, promote all parameter inputs and outputs to top level.  Everything has unique names at this point so we should be good. 
    bs = battSurrogate.BatterySurrogate()
    model.add_subsystem('surr_batt', bs, promotes=["*"])
    
    # Add Mass 
    mass_comp = om.ExecComp("Mass = Mass__Battery + 1")
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

def PlanarSystemDynamicPhase(tx):
    
    # Instantiate a Dymos Trajectory
    model_path = os.path.join(os.path.dirname(__file__), 'PlanarPT/PlanarPowerTrainModel')
    pt_meta = dmm.ImportMetadata(model_path)
    
    # Instantiate a Phase and add it to the Trajectory.
    # Here the transcription is necessary but not particularly relevant.
    phase = dm.Phase(ode_class=PlanarSystemDynamicModel, transcription=tx)
    
    ## Add PowerTrain Information
    phase = dmm.ModifyPhase(phase, pt_meta, openmdao_path="PT", include_disturbances=False, state_opts = {}, control_opts = {}, disturbance_opts={"val":0}, parameter_opts = {})
    
    ## Add Body Model Information
    phase = bm.ModifyPhase(phase, openmdao_path="BM", declare_controls=False)
    
    return phase

