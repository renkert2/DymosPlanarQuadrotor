# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.pickling as my_pickle
import SUPPORT_FUNCTIONS.plotting as plotting
import OPTIM.Search as search
import matplotlib as mpl
import matplotlib.pyplot as plt
from ARG_Research_Python import my_plt
import numpy as np

import PlanarSystem as PS
import Recorders as R
from GraphTools_Phil_V2.OpenMDAO import Param

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__, dirname="Output_07282022")
reader = search.SearchReader(output_dir = "search_output")

export_dir = r"C:\Users\renkert2\Documents\ARG_Research\CBDOConferencePaper\Case Study\MinimumTime\DiscreteDomain"

mpl.rcParams["font.serif"] = "Times"
mpl.rcParams["axes.titlesize"] = 8
mpl.rcParams["axes.labelsize"] = 8
mpl.rcParams["legend.fontsize"] = 8
mpl.rcParams['font.size'] = 8
mpl.rcParams["lines.linewidth"] = 2
mpl.rcParams["savefig.bbox"] = 'tight'
mpl.rcParams["savefig.pad_inches"] = 0.025

#%% Read Search Result
result = reader.result

print(result)

#%% Reattach component searchers, need to fix
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

target_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "SystemOptimization", "Output_07282022", "pv_opt.pickle")
with open(target_path, 'rb') as f:
    target = my_pickle.renamed_load(f)

comp_searchers = {}
for (k,v) in s.surrogates.items():
    comp_searchers[k] = search.ComponentSearcher(v)
    comp_searchers[k].set_target(target)

result.config_searcher.component_searchers = comp_searchers


#%%
case_reader_0 = reader.case_reader
case_reader_1 = R.Reader(os.path.join(reader.output_dir, "search_cases_1.sql"))

base_case = case_reader_0.get_case("base_case")
final_case = case_reader_1.get_case(result.opt_iter.case_name)

R.delta_table(base_case, final_case)

# input_opt_reader = om.CaseReader(os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "InputOptimization", "Output_07052022", "input_opt_cases.sql"))
# input_opt_case = input_opt_reader.get_case("input_opt_final")

sys_opt_reader = om.CaseReader(os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_MISSION_1", "SystemOptimization", "Output_07282022", "sys_opt_cases.sql"))
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
    
#%% Algorithm Performance
fevals = [x.func_evals for x in result.iterations]

total_fevals = sum(fevals)
total_fevals_optiter = sum(fevals[:result.opt_iter.iteration + 1])

print(f"Total func evals: {total_fevals}")
print(f"Func Evals to find Optimal Configuration: {total_fevals_optiter}")


#%%
fig, ax = result.plot()
fig.set_size_inches(3.25,2.75)
ax[1].legend(loc="lower right")
ax[1].set_ylabel("Distance Metric")
ax[1].set_xlabel("Iteration")
my_plt.export(fig, fname="discrete_search_result", directory=export_dir)

#%%
end_sol = Param.ParamValSet()
with open(os.path.join(init.HOME_PATH, "STUDIES", "FlightTimePerPrice", "discrete_solution_paramvals.json")) as source:
    end_sol.load(source)
    
figs, mkropts = result.plotDesignSpace()
names = ["batt_design_space_search", "motor_design_space_search", "prop_design_space_search"]
comps = ["Battery", "PMSMMotor", "Propeller"]
labels = [("Series Cells", "Capacity (mAh)"), ("Speed Constant (RPM/V)", "Wind Resistance ($\Omega$)"), ("Diameter (m)", "Pitch (m)")]
for c,l,f in zip(comps, labels, figs):
    f.suptitle(None)
    f.set_size_inches(3.25, 2.25, forward=True)
    
    ax = f.get_axes()[0]
    ax.set_xlabel(l[0])
    ax.set_ylabel(l[1])
    
    s_ = s[c]
    pv = [p.get_compatible(end_sol) for p in s_.boundary.args]
    prev_pnts = [x.val for x in pv]
    mkropts["markerfacecolor"] = 'mediumblue'
    mkropts["label"] = 'Endurance'
    
    l, = ax.plot(*prev_pnts, **mkropts)
    
    bnd = ax.get_children()[1]
    bnd.set_label("Constraint")

    if c == "Propeller":
        ax.axvline(0.356, color='r')
        ax.legend(loc="lower right")
    elif c == "Battery":
        ax.legend(loc="upper left")
    elif c == "PMSMMotor":
        ax.legend(loc="lower right")
    figs.append(f)


#%%
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=export_dir)

#%%
def mllabel(x):
    return r"\begin{center}" + x + r"\end{center}"

graphics = plotting.timeseries_plots(sim=[base_case, final_case], phases=[f"phase{i}" for i in range(5)], title="Discrete Search Result Optimization", legend=["Initial", "Opt. Config."])
names = ["opt_config_body_states", "opt_config_powertrain_states", "opt_config_inverter_currents", "opt_config_inverter_inputs"]
lbls = [[r"Horizontal \\ Position (m)", r"Vertical \\ Position (m)", r"Angular \\ Position (rad)"], None, None, None]
figs = []
for i,(f,a) in enumerate(graphics):
    if lbls[i]:
        for j,a_ in enumerate(a):
            a_.set_ylabel(mllabel(lbls[i][j]))
    f.suptitle(None)
    f.set_size_inches(3.25,3.5)
    
    figs.append(f)
    
    
#%%
for (f,n) in zip(figs,names):
    my_plt.export(f, fname=n, directory=export_dir)