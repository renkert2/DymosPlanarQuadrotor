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

name = "sys_opt_cases"
sim_name= name+"_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")


#%% Trajectory Comparisons
# graphics = plotting.timeseries_plots(sim_cases, title="System Optimization")


# #%% Optimization Variables
# opt_vars=["params.N_s__Battery", "params.Q__Battery", "params.kV__Motor", "params.Rm__Motor", "params.D__Propeller", "params.P__Propeller"]
# plotting.iterplots(reader, opt_vars, labels=["$N_s$", "$Q$ (mAh)", "$kV$ (RPM/V)", "$Rm$ ($\Omega$)", "$D$ (m)", "$P$ (m)"], title="System Optimization: Design Variables", save=False)

# #%% Boundary Plots
# import PlanarSystem as PS
# pp = PS.PlanarSystemParams()
# ps = PS.PlanarSystemSurrogates(pp)
# ps.setup()
# for s in ps.surrogates.values():
#     plotting.boundaryiterplots(s, reader)

#%% Comparison to Other Optimizations
# Case Paths:
reader_names = [x+"_opt_cases_sim.sql" for x in ["batt", "motor", "prop"]]
legends = ["Opt Battery", "Opt Motor", "Opt Propeller"]
colors = ["g", "r", "m"]

study_path = os.path.join(init.HOME_PATH, "STUDIES")
reader_paths = [os.path.join(study_path, x, "Output") for x in ["BatteryOptimization\BattOpt", "MotorOptimization\MotorOpt", "PropellerOptimization\PropellerOpt"]]

readers = [om.CaseReader(os.path.join(x[0], x[1])) for x in zip(reader_paths, reader_names)]
other_cases = [x.get_cases("problem")[1] for x in readers] # Final Solution

graphics = plotting.timeseries_plots([sim_cases[0], *other_cases, sim_cases[1]], title="System Optimization")


