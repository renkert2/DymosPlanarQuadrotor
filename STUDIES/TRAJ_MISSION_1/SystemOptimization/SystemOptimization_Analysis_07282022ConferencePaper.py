# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 15:10:11 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
from ARG_Research_Python import my_plt
import matplotlib as mpl
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.slugify as slug
import os
import Recorders as R

init.init_output(__file__, dirname="Output_07282022")
export_dir = r"C:\Users\renkert2\Documents\ARG_Research\CBDOConferencePaper\Case Study\MinimumTime\ContinuousDomain\SystemOptimization"

mpl.rcParams["font.serif"] = "Times"
mpl.rcParams['font.size'] = 8
mpl.rcParams["lines.linewidth"] = 2
mpl.rcParams["savefig.bbox"] = 'tight'
mpl.rcParams["savefig.pad_inches"] = 0.025

name = "sys_opt_cases"
sim_name= name+"_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")

#%% Node Study
case = cases[-1]

path_list = ['traj.phases.phase0.collocation_constraint.defects:BM_x', 'traj.phases.phase0.indep_states.states:BM_x', 'traj.phases.phase0.interleave_comp.all_values:states:BM_x', 'traj.phases.phase0.state_interp.state_col:BM_x', 'traj.phases.phase0.timeseries.states:BM_x']
for p in path_list:
    print(p, len(case.get_val(p)))

control_list = ['traj.phases.phase0.timeseries.controls:PT_u1','traj.phases.phase0.control_group.indep_controls.controls:PT_u1','traj.phases.phase0.control_group.control_interp_comp.control_values:PT_u1','traj.phases.phase0.continuity_comp.defect_controls:PT_u1']
for p in control_list:
    print(p, len(case.get_val(p)))
#%%
(d,t_latex) = reader.delta_table()

#%% Trajectory Comparisons
graphics = plotting.timeseries_plots(prob = cases, sim=sim_cases, phases=[f"phase{i}" for i in range(5)], title="System Optimization")

# CHeck Battery Current Constraint
#graphics = plotting.timeseries_plots(prob = cases, sim=sim_cases,  phases=[f"phase{i}" for i in range(5)], title="System Optimization", show_plts=[1])


#%% Optimization Variables
# opt_vars=["params.N_s__Battery", "params.Q__Battery", "params.kV__Motor", "params.Rm__Motor", "params.D__Propeller", "params.P__Propeller"]
# (fig, ax) = plotting.iterplots(reader, opt_vars, labels=["$N_s$", "$Q$ (mAh)", "$kV$ (RPM/V)", "$Rm$ ($\Omega$)", "$D$ (m)", "$P$ (m)"], title="System Optimization: Design Variables", save=False)

# my_plt.export(fig, fname="sys_opt_des_var_iters", directory=os.getcwd())
#%% Boundary Plots
import PlanarSystem as PS
from GraphTools_Phil_V2.OpenMDAO import Param
pp = PS.PlanarSystemParams()
ps = PS.PlanarSystemSurrogates(pp)
ps.setup()

prev_sol = Param.ParamValSet()
with open(os.path.join(init.HOME_PATH, "STUDIES", "FlightTimePerPrice", "continuous_solution.json")) as source:
    prev_sol.load(source)

comps = ["Battery", "PMSMMotor", "Propeller"]
labels = [("Series Cells", "Capacity (mAh)"), ("Speed Constant (RPM/V)", "Wind Resistance ($\Omega$)"), ("Diameter (m)", "Pitch (m)")]
figs = []
for c,l in zip(comps, labels):
    s = ps[c]
    (fig, ax, mkropts) = plotting.boundaryiterplots(s, reader, markersize=10, itermarkersize=5)
    
    fig.suptitle(None)
    fig.set_size_inches(3.25, 2.25, forward=True)
    ax.set_xlabel(l[0])
    ax.set_ylabel(l[1])
    
    prev_pnts = [prev_sol[x].val for x in [x.name for x in s.boundary.args]]
    l, = ax.plot(*prev_pnts, markeredgecolor="blue",  label="Endurance", **mkropts)
    
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

for fig,c in zip(figs,comps):
    my_plt.export(fig,  fname=f"sys_opt_designspace_{c}", directory=export_dir)

#%%


#%% Comparison to Other Optimizations
plt.close('all')


legends = ["Initial", "Opt System"]
graphics = plotting.timeseries_plots(sim=[sim_cases[0], sim_cases[1]], title="System Optimization", legend = legends, phases=[f'phase{i}' for i in range(5)])

pltnames = ["Body States", "Powertrain States", "Inverter Currents", "Inverter Inputs"]
pltslugs = [slug.slugify(x) for x in pltnames]
    
#%%
for i,g in enumerate(graphics):
    fig = g[0]
    my_plt.export(fig, fname=f"sys_opt_trajectories_{pltslugs[i]}", directory=wdir)
    
#%% Analyze Braking in Optimal Design
get_wrapper = lambda path: reader.get_val_multiphase(cases[1], path, phases=range(5))
t = get_wrapper("traj.{}.timeseries.time")

# Check
# plt.figure(1)
# x = get_wrapper("traj.{}.timeseries.states:BM_x")
# y = get_wrapper("traj.{}.timeseries.states:BM_y")
# plt.plot(t,x,t,y)

# Rotor Speeds
# plt.figure(2)
# omega_1 = get_wrapper("traj.{}.timeseries.states:PT_x2")
# omega_2 = get_wrapper("traj.{}.timeseries.states:PT_x3")

# plt.plot(t,omega_1,t,omega_2)

# Currents
i_1 = get_wrapper("traj.{}.timeseries.outputs:PT_a3")
i_2 = get_wrapper("traj.{}.timeseries.outputs:PT_a5")
i_bus = get_wrapper("traj.{}.timeseries.outputs:PT_a2")
i_bus_max = cases[1].get_val("params.MaxDischarge__Battery")
i_motor_1 = get_wrapper("traj.{}.timeseries.outputs:PT_a7")
i_motor_2 = get_wrapper("traj.{}.timeseries.outputs:PT_a8")

# Voltages
v_bus = get_wrapper("traj.{}.timeseries.outputs:PT_a1")
v_1 = get_wrapper("traj.{}.timeseries.outputs:PT_a4")
v_2 = get_wrapper("traj.{}.timeseries.outputs:PT_a6")

# Power
P_bus = i_bus*v_bus
P_inv_1 = i_motor_1 * v_1
P_inv_2 = i_motor_2 * v_2 

# Thrusts
T_1 = get_wrapper("traj.{}.timeseries.outputs:PT_y1")
T_2 = get_wrapper("traj.{}.timeseries.outputs:PT_y3")

# plt.figure(3)
# plt.plot(t,i_1,t,T_1)
# plt.axhline(y=80, linestyle='--', color='r')

plt.figure()
plt.plot(t,i_bus)
plt.axhline(y=i_bus_max, linestyle="--", color='r')

# plt.figure(4)
# plt.plot(t,i_bus, t, i_1 + i_2)
# plt.legend(["Bus", "Inverter Sum"])

# plt.figure()
# plt.plot(t, P_bus, t, P_inv_1 + P_inv_2)
# plt.legend(["Bus Power", "Inverter Power (Sum)"])





