# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:10:11 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os

init.init_output(__file__)

name = "batt_opt_cases"
sim_name= name+"_sim"

reader = om.CaseReader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")


#%% Trajectory Comparisons
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']],
                                labels=['$x$', '$y$', r'$\theta$'], 
                                title="Battery Optimization: Body States", 
                                legend=["Initial", "Final"])

#%% Internal States

vars = ["states:PT_x1", "outputs:PT_a1", "outputs:PT_a2"]
labels = ["SOC", "Bus Voltage", "Battery Current (A)"]
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=vars,
                                labels=labels, 
                                title="Battery Optimization: Powertrain States ", 
                                legend=["Initial", "Final"])

vars = ["outputs:PT_a3", "outputs:PT_a5"]
labels = ["Inverter 1 Current (A)", "Inverter 2 Current (A)"]
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=vars,
                                labels=labels, 
                                title="Battery Optimization: Inverter Currents", 
                                legend=["Initial", "Final"])

vars = [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']]
labels = ["Inverter 1 Input", "Inverter 2 Input"]
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=vars,
                                labels=labels, 
                                title="Battery Optimization: Inverter Inputs", 
                                legend=["Initial", "Final"])


#%% Optimization Variables
opt_vars=["params.N_s__Battery", "params.Q__Battery"]
plotting.iterplots(reader, opt_vars, labels=["$N_s$", "$Q$ (mAh)"], title="Battery Optimization: Design Variables", save=False)

