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
import Recorders as R

init.init_output(__file__)

name = "motor_opt_cases"
sim_name= name+"_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")


#%% Trajectory Comparisons
graphics = plotting.timeseries_plots(sim_cases, title="Motor Optimization")


#%% Optimization Variables
opt_vars=["params.kV__Motor", "params.Rm__Motor"]
plotting.iterplots(reader, opt_vars, labels=["$kV$ (RPM/V)", "$Rm$ ($\Omega$)"], title="Motor Optimization: Design Variables", save=False)

#%% Boundary Plots
import PlanarSystem as PS
pp = PS.PlanarSystemParams()
ps = PS.PlanarSystemSurrogates(pp)
ps.setup()
pb = ps["PMSMMotor"]
plotting.boundaryiterplots(pb, reader)




