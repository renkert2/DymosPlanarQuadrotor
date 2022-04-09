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


#%% Trajectory Comparisons
graphics = plotting.timeseries_plots(sim_cases, title="Battery Optimization")


#%% Optimization Variables
opt_vars=["params.N_s__Battery", "params.Q__Battery"]
plotting.iterplots(reader, opt_vars, labels=["$N_s$", "$Q$ (mAh)"], title="Battery Optimization: Design Variables", save=False)

#%% Boundary Plots
import PlanarSystem as PS
pp = PS.PlanarSystemParams()
ps = PS.PlanarSystemSurrogates(pp)
ps.setup()
pb = ps["Battery"]
#%%
(fig, ax) = pb.plot_boundary_2D()
fig.suptitle(f"Design Space: {pb.comp_name}")
opt_vars = [f"params.{p.strID}" for p in pb.boundary.args]
(iters, vals) = reader.get_itervals(opt_vars)
ax.plot(vals[0], vals[1], '.-k', markersize=10, linewidth=1)

mkropts = {"marker":"o", "markersize":15, "markerfacecolor":"none", "markeredgewidth":2, "color":"k"}
# Initial Point
x_0 = [v[0] for v in vals]
l_i, = ax.plot(*x_0, markeredgecolor="orange",  label="Initial", **mkropts)

# Initial Point
x_f = [v[-1] for v in vals]
l_f, = ax.plot(*x_f, markeredgecolor="green",  label="Final", **mkropts)

ax.legend(handles=[l_i, l_f])




