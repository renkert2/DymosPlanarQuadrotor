# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search
import matplotlib.pyplot as plt
import numpy as np
import my_plt
import PlanarSystem as PS

import logging
logging.basicConfig(level=logging.INFO)

export_dir = r"C:\Users\renkert2\Box\ARG_Student_Reports\Philip Renkert\THESIS\Case Study\MinimumTime\DiscreteDomain"

init.init_output(__file__)
search_out_dir = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "DiscreteSearch", "Output_07052022", "search_output")
reader = search.SearchReader(output_dir = search_out_dir)

#%% Read Search Result
result = reader.result

print(result)

#%% Reattach component searchers, need to fix
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "SystemOptimization", "Output_07052022", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = pickle.load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

result.config_searcher.component_searchers = comp_searchers


#%%
case_reader = reader.case_reader
[dt_dict, dt_latex] = case_reader.delta_table(init_case_name="base_case", final_case_name=result.opt_iter.case_name)
print(dt_latex)

base_case = case_reader.get_case("base_case")
final_case = case_reader.get_case(result.opt_iter.case_name)


input_opt_reader = om.CaseReader(os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "InputOptimization", "Output_07052022", "input_opt_cases.sql"))
input_opt_case = input_opt_reader.get_case("input_opt_final")

sys_opt_reader = om.CaseReader(os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "SystemOptimization", "Output_07052022", "sys_opt_cases.sql"))
sys_opt_initial = sys_opt_reader.get_case("sys_opt_initial")
#%%
pv = result.opt_iter.config.data
for param in p:
    pv_ = param.get_compatible(pv)
    if pv_:
        init_val = param.val
        final_val = pv_.val
        rel_change = (final_val - init_val)/init_val
        print(f"{param.strID}: Initial={init_val}, Final={final_val}, change={rel_change}")

#%% Thrust Ratio
trdat = []
for case in [sys_opt_initial, final_case]:
    dat = {}
    dat["tmax"] = case.get_val("constraint__thrust_ratio.TMax")
    dat["tr"] = case.get_val("constraint__thrust_ratio.TR")
    dat["mass"] = case.get_val("params.Mass__System")
    
    print("TMax: ", dat["tmax"], "Mass: ", dat["mass"], "TR: ", dat["tr"])

#%% Rotational Inertia
trdat = []
for case in [sys_opt_initial, final_case]:
    dat = {}
    dat["Is"] = case.get_val("params.I__System")
    dat["Jr"] = case.get_val("params.J_r__MotorProp")
    dat["J_motor"] = case.get_val("params.J__Motor")
    dat["J_prop"] = case.get_val("params.J__Propeller")
    dat["mass_motor"] = case.get_val("params.Mass__Motor")
    dat["mass_prop"] = case.get_val("params.Mass__Propeller")
    
    print(dat)

#%%
fig, ax = result.plot()
fig.set_size_inches(6,4)
ax[1].legend(loc="lower right")
ax[1].set_ylabel("Distance Metric")
ax[1].set_xlabel("Iteration")
my_plt.export(fig, fname="discrete_search_result", directory=export_dir)

#%% Function Evaluations at Optimal Config
opt_iters = result.iterations[:70]
total_fevals = sum([x.func_evals for x in opt_iters])
print(f"Func Evals to find Optimal Configuration: {total_fevals}")



#%%
import Param
end_sol = Param.ParamValSet()
with open(os.path.join(init.HOME_PATH, "STUDIES", "FlightTimePerPrice", "discrete_solution_paramvals.json")) as source:
    end_sol.load(source)
    
figs, mkropts = result.plotDesignSpace()
names = ["batt_design_space_search", "motor_design_space_search", "prop_design_space_search"]
comps = ["Battery", "PMSMMotor", "Propeller"]
labels = [("Series Cells", "Capacity (mAh)"), ("Speed Constant (RPM/V)", "Wind Resistance ($\Omega$)"), ("Diameter (m)", "Pitch (m)")]
for c,l,f in zip(comps, labels, figs):
    f.suptitle(None)
    f.set_size_inches(6, 4, forward=True)
    
    ax = f.get_axes()[0]
    ax.set_xlabel(l[0])
    ax.set_ylabel(l[1])
    
    s_ = s[c]
    pv = [p.get_compatible(end_sol) for p in s_.boundary.args]
    prev_pnts = [x.val for x in pv]
    mkropts["markerfacecolor"] = 'mediumblue'
    mkropts["label"] = 'Endurance'
    
    l, = ax.plot(*prev_pnts, **mkropts)
    
    bnd = ax.get_children()[2]
    bnd.set_label("Constraint")

    if c == "Propeller":
        ax.axvline(0.356, color='r')
        ax.legend(loc="lower right")
    elif c == "Battery":
        ax.legend(loc="upper left")
    elif c == "PMSMMotor":
        ax.legend(loc="lower right")
    
    figs.append(fig)


#%%
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=export_dir)

#%% Plot Heatmaps of Mean Obj. Value
figs = result.plotCompHeatmat(stat_func=np.mean, stat_func_label="Mean Obj. Value")
names = ["batt_design_space_meanval", "motor_design_space_meanval", "prop_design_space_meanval"]
import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))

#%% Plot Heatmaps ob Min Obj. Value
figs = result.plotCompHeatmat(stat_func=np.min, stat_func_label="Min Obj. Value")
names = ["batt_design_space_minval", "motor_design_space_minval", "prop_design_space_minval"]
import my_plt
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=os.path.join(weekly_reports.WEEKLY_REPORTS, "Renkert_WeeklyReport_06292022"))
    
#%%
result.showTopComps()

#%%
import SUPPORT_FUNCTIONS.plotting as plotting
graphics = plotting.timeseries_plots(sim=[base_case, final_case], phases=[f"phase{i}" for i in range(5)], title="Discrete Search Result Optimization", legend=["Initial", "Opt. Config."])
names = t = ["opt_config_body_states", "opt_config_powertrain_states", "opt_config_inverter_currents", "opt_config_inverter_inputs"]
figs = []
for f,a in graphics:
    f.suptitle(None)
    f.set_size_inches(6,4.5)
    figs.append(f)
    
#%%
for f,n in zip(figs,names):
    my_plt.export(f, fname=n, directory=export_dir)
    