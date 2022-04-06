# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np

import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.timing as timing
import ProblemTemplates as PT

init.init_output(__file__)

prob = PT.StepProblem()

# Run the Optimization Problem
run_driver = timing.simple_timer(prob.run_driver)
run_driver()
prob.record('final')
prob.cleanup()

traj = prob.model.traj
sim_out = traj.simulate(times_per_seg=50)

#%% Plots
my_plt.subplots(sim_out, prob, path='traj.phase0.timeseries',
             vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']] + [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']],
             labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"], 
             title="Planar Quadrotor Input Optimization", save=True)
