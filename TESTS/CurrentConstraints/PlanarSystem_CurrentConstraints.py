# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 15:46:01 2022

@author: renkert2
"""

import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np

import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.timing as timing
import Constraints as C
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps

init.init_output(__file__)

def run_prob(model_maker, name):
    traj = T.Step()
    traj.setup()
    
    model = model_maker(traj)
    
    prob = P.Problem(model=model, planar_traj = traj)
    rec = R.Recorder(name=f"{name}_cases.sql")
    rec.add_prob(prob)
    
    prob.setup()
    
    prob.init_vals()
    prob.run_driver()
    
    rec.add_traj(traj.traj)
    rec.record(case=f'final_{name}')
    
    prob.cleanup()
    return prob, traj

def model_nocon(traj):
    cons = C.ConstraintSet()
    model = ps.PlanarSystemModel(traj.traj, cons = cons)
    return model

def model_battcon(traj):
    cons = C.ConstraintSet()
    c = C.BatteryCurrent()
    cons.add(c)
    model = ps.PlanarSystemModel(traj.traj, cons = cons)
    batt_max_i = model._params["MaxDischarge__Battery"]
    batt_max_i.dep=False
    batt_max_i.val=42.0
    batt_max_i.x0=42.0
    
    return model

def model_invcon(traj):
    cons = C.ConstraintSet()
    c = C.InverterCurrent()
    c._ub = 22
    cons.add(c)
    model = ps.PlanarSystemModel(traj.traj, cons = cons)
  
    return model

outs = []
for (conmdl, name) in zip([model_nocon, model_battcon, model_invcon], ["nocon", "battcon", "invcon"]):
    out = run_prob(conmdl, name)
    outs.append(out)



