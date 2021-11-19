# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 16:07:54 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import PlanarBody.PlanarQuadrotorODE as bm
import PlanarPT.PlanarPTModel as pt 
import DymosModel as dmm
import dymos as dm
import os


class PlanarSystemModel(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_subsystem(name="PT", subsys=pt.PlanarPTModel(num_nodes=nn))
        self.add_subsystem(name="BM", subsys=bm.PlanarQuadrotorODE(num_nodes=nn))
        
        self.connect("PT.y12", "BM.u_1")
        self.connect("PT.y14", "BM.u_2")

def PlanarSystemPhase(tx):
    
    # Instantiate a Dymos Trajectory
    model_path = os.path.join(os.path.dirname(__file__), 'PlanarPT/PlanarPowerTrainModel')
    pt_meta = dmm.ImportMetadata(model_path)
    
    # Instantiate a Phase and add it to the Trajectory.
    # Here the transcription is necessary but not particularly relevant.
    phase = dm.Phase(ode_class=PlanarSystemModel, transcription=tx)
    
    ## Add PowerTrain Information
    phase = dmm.ModifyPhase(phase, pt_meta, openmdao_path="PT", include_disturbances=False, state_opts = {}, control_opts = {}, disturbance_opts={"val":0}, parameter_opts = {})
    
    ## Add Body Model Information
    phase = bm.ModifyPhase(phase, openmdao_path="BM", declare_controls=False)
    
    return phase