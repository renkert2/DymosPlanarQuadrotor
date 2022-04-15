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
import SUPPORT_FUNCTIONS.slugify as slug
import os
import Recorders as R

init.init_output(__file__)

name = "sys_opt_cases"
sim_name= name+"_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")

#%%
(d,t_latex) = reader.delta_table()

#%% Trajectory Comparisons
graphics = plotting.timeseries_plots(prob = cases, sim=sim_cases, title="System Optimization")


#%% Optimization Variables
opt_vars=["params.N_s__Battery", "params.Q__Battery", "params.kV__Motor", "params.Rm__Motor", "params.D__Propeller", "params.P__Propeller"]
(fig, ax) = plotting.iterplots(reader, opt_vars, labels=["$N_s$", "$Q$ (mAh)", "$kV$ (RPM/V)", "$Rm$ ($\Omega$)", "$D$ (m)", "$P$ (m)"], title="System Optimization: Design Variables", save=False)

my_plt.export(fig, fname="sys_opt_des_var_iters", directory=os.getcwd())
#%% Boundary Plots
import PlanarSystem as PS
import Param
pp = PS.PlanarSystemParams()
ps = PS.PlanarSystemSurrogates(pp)
ps.setup()

prev_sol = Param.ParamValSet()
with open(os.path.join(init.HOME_PATH, "STUDIES", "FlightTimePerPrice", "continuous_solution.json")) as source:
    prev_sol.load(source)

comps = ["Battery", "PMSMMotor", "Propeller"]
for c in comps:
    s = ps[c]
    (fig, ax, mkropts) = plotting.boundaryiterplots(s, reader)
    
    prev_pnts = [prev_sol[x].val for x in [x.name for x in s.boundary.args]]
    l, = ax.plot(*prev_pnts, markeredgecolor="blue",  label="Endurance", **mkropts)
    ax.legend()
    
    my_plt.export(fig, fname=f"sys_opt_designspace_{c}", directory=os.getcwd())

#%%


#%% Comparison to Other Optimizations
# Case Paths:
reader_names = [x+"_opt_cases_sim.sql" for x in ["batt", "motor", "prop"]]


study_path = os.path.join(init.HOME_PATH, "STUDIES")
reader_paths = [os.path.join(study_path, x, "Output") for x in ["BatteryOptimization\BattOpt", "MotorOptimization\MotorOpt", "PropellerOptimization\PropellerOpt"]]

readers = [om.CaseReader(os.path.join(x[0], x[1])) for x in zip(reader_paths, reader_names)]
other_cases = [x.get_cases("problem")[1] for x in readers] # Final Solution

legends = ["Initial", "Opt Battery", "Opt Motor", "Opt Propeller", "Opt System"]
graphics = plotting.timeseries_plots([sim_cases[0], *other_cases, sim_cases[1]], title="System Optimization", legend = legends)

pltnames = ["Body States", "Powertrain States", "Inverter Currents", "Inverter Inputs"]
pltslugs = [slug.slugify(x) for x in pltnames]
for i in plt.get_fignums():
    fig = plt.figure(i)
    fig.set_figheight(1.25*fig.get_figheight())
    my_plt.export(fig, fname=f"sys_opt_trajectories_{pltslugs[i-1]}", directory=os.getcwd())
    
