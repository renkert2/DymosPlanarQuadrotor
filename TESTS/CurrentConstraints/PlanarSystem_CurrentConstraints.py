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



def prob_nocon():
    traj = T.Step()
    traj.setup()
    
    cons = C.ConstraintSet()
    model = ps.PlanarSystemModel(traj.traj, cons = cons)
    
    prob = P.Problem(model=model, planar_traj = traj)
    rec = R.Recorder(name="nocon_cases.sqr")
    rec.add_to_prob(prob)
    prob.setup()
    prob.init_vals()
    
    prob.run_driver()
    
    prob.record('final_nocon')
    return prob, traj

def prob_battcon():
    traj = T.Step()
    traj.setup()
    
    cons = C.ConstraintSet()
    c = C.BatteryCurrent()
    cons.add(c)
    model = ps.PlanarSystemModel(traj.traj, cons = cons)
    batt_max_i = model._params["MaxDischarge__Battery"]
    batt_max_i.dep=False
    batt_max_i.val=42.0
    batt_max_i.x0=42.0
    
    prob = P.Problem(model=model, planar_traj = traj)
    rec = R.Recorder(name="battcon_cases.sqr")
    rec.add_to_prob(prob)
    prob.setup()
    prob.init_vals()
    
    prob.run_driver()
    
    prob.record('final_battcon')
    return prob, traj

def prob_invcon():
    traj = T.Step()
    traj.setup()
    
    cons = C.ConstraintSet()
    c = C.InverterCurrent()
    c._ub = 10
    cons.add(c)
    model = ps.PlanarSystemModel(traj.traj, cons = cons)
  
    prob = P.Problem(model=model, planar_traj = traj)
    rec = R.Recorder(name="invcon_cases.sqr")
    rec.add_to_prob(prob)
    prob.setup()
    prob.init_vals()
    
    prob.run_driver()
    
    prob.record('final_invcon')
    return prob, traj

outs = []
for probfun in [prob_nocon, prob_battcon, prob_invcon]:
    out = probfun()
    outs.append(outs)
    

#%% Simulations
#sim = traj.traj.simulate()

#%% Print
#my_plt.subplots(sim, prob, path='traj.phase0.timeseries', vars=["outputs:PT_a2"], labels=["Battery Current"], title="Current Constraints", save=False)
#plt.show()


