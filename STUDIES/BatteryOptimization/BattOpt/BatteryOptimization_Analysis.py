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

name = "batt_opt_cases"
sim_name= name+"_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")

#%% Design Variable Results
(d,t_latex) = reader.delta_table()

#%% Trajectory Comparisons
graphics = plotting.timeseries_plots(sim_cases, title="Battery Optimization")


#%% Optimization Variables
opt_vars=["params.N_s__Battery", "params.Q__Battery"]
fig,ax = plotting.iterplots(reader, opt_vars, labels=["$N_s$", "$Q$ (mAh)"], title="Battery Optimization: Design Variables", save=False)

my_plt.export(fig, fname="batt_opt_des_var_iters", directory=os.getcwd())

#%% Boundary Plots
import PlanarSystem as PS
pp = PS.PlanarSystemParams()
ps = PS.PlanarSystemSurrogates(pp)
ps.setup()
pb = ps["Battery"]

fig, ax, mkropts = plotting.boundaryiterplots(pb, reader)

# Append boundary plots with solution to Flight Time per Price Problem
import Param

prev_sol = Param.ParamValSet()

with open(os.path.join(init.HOME_PATH, "STUDIES", "FlightTimePerPrice", "continuous_solution.json")) as source:
    prev_sol.load(source)

#
prev_pnts = [prev_sol[x].val for x in [x.name for x in pb.boundary.args]]

l, = ax.plot(*prev_pnts, markeredgecolor="blue",  label="Endurance", **mkropts)
leg_hndls = ax.get_legend().legendHandles

ax.legend()

#%%
my_plt.export(fig, fname="batt_opt_designspace", directory=os.getcwd())