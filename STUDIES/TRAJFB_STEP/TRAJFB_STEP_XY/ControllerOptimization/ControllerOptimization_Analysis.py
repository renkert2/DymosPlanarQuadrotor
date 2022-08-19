#%%
import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
from ARG_Research_Python import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os
import Recorders as R
import numpy as np
import re

init.init_output(__file__)

input_opt_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_STEP", "InputOptimization", "Output")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")

name = "controller_opt_cases"
sim_name = "controller_opt_cases_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(sim_name+".sql")
sim_cases = sim_reader.get_cases("problem")

#%%
(d,t_latex) = reader.delta_table()
#%% 
print(reader.list_cases())

#%% Trajectory Comparisons
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']],
                                labels=['$x$', '$y$', r'$\theta$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])
fig.set_figheight(5)
fig.set_figwidth(6)
my_plt.export(fig, "step_xy_dynamicsconvergence_zeroprop100UB")

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"controls:{x}" for x in  ['CTRL_x_T', 'CTRL_y_T', "CTRL_v_x_T", "CTRL_v_y_T"]],
                                labels=['$x_T$', '$y_T$', "$\dot{x}_T$", "$\dot{y}_T$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_u_1', 'CTRL_u_2'],
                                labels=['$u_1$', '$u_2$'], 
                                title="Inverter Inputs", 
                                legend=["Initial", "Final"])
#(f, axes) = plotting.subplots(None, input_opt_final, path='traj.phase0.timeseries', save=False, axes=axes,
#                                vars=['controls:PT_u1', 'controls:PT_u2'])

#for ax in axes:
#    ax.legend(["Feedback",None, "Optimal",None])
    
#my_plt.export(fig, "step_xy_inputs")

#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_F_star_x', 'CTRL_F_star_y', 'CTRL_T_star'],
                                labels=['$F^*_x$', '$F^*_y$', "$T^*$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_theta_star', 'CTRL_tau_z_star'],
                                labels=['$\theta^*$', '$\tau^*_z$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])
#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_omega_1_star', 'CTRL_omega_2_star', "states:PT_x2", "states:PT_x3"],
                                labels=['$\omega^*_1$', '$\omega^*_2$', '$\omega_1$', '$\omega_2$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_e_omega_1', 'CTRL_e_omega_2'],
                                labels=[r'$e_{\omega_1}$', r'$e_{\omega_2}$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])
#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['states:CTRL_e_omega_1_I', 'states:CTRL_e_omega_1_I'],
                                labels=[r'$I_{\omega_1}$', r'$I_{\omega_2}$'], 
                                title="Speed Controller Integrator", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['states:CTRL_e_omega_1_I', 'states:CTRL_e_omega_1_I'],
                                labels=[r'$I_{\omega_1}$', r'$I_{\omega_2}$'], 
                                title="Speed Controller Integrator", 
                                legend=["Final"])

#%% Position Reference Following
(fig, axes) = plotting.subplots(None, cases, path='traj.phase0.timeseries', save=False, plot_dividers=False,
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'CTRL_e_T_I']],
                                labels=['$x$', '$y$', 'Accum. Error'], 
                                title="Position Reference Following")
(f, axes_2) = plotting.subplots(None, cases[-1], path='traj.phase0.timeseries', save=False, axes=axes[range(2)], plot_dividers=False,
                                 vars=['controls:CTRL_x_T', 'controls:CTRL_y_T'])
                                 
axes[0].legend(["Initial", "Final", "Reference"])

fig.set_figheight(5)
fig.set_figwidth(6)
my_plt.export(fig, "step_xy_referencetracking_zeroprop100UB")

#%% Rotor Speed Reference Following
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=["states:PT_x2", "states:PT_x3"],
                                labels=['$\omega_1$', '$\omega_2$'], 
                                title="Speed Reference Following")
# (f, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, axes=axes,
#                                 vars=['CTRL_omega_1_star', 'CTRL_omega_2_star'])

# for ax in axes:
#     ax.legend(["State",None, "Reference",None])

#my_plt.export(fig, "step_x_rotorspeed_stable")

#%% Iter Vals

driver_cases = reader.get_cases('driver', recurse=False)
iters = np.arange(len(driver_cases))

plt.figure(1)
var = 'params.k_d_r__Controller'
var_data = np.zeros((len(iters),))
for j, case in enumerate(driver_cases):
    var_data[j] = case[var][-1]
    
plt.plot(iters,var_data)
plt.xlabel("Iteration")
plt.ylabel("$k_{p,r}$")
my_plt.export(plt.figure(1), fname="iter_desvar_vals_singlegain")

#%%
plt.figure(2)
var = 'traj.phase0.states:CTRL_e_T_I'
var_data = np.zeros((len(iters),))
for j, case in enumerate(driver_cases):
    var_data[j] = case[var][-1]
    
plt.plot(iters,var_data)
plt.xlabel("Iteration")
plt.ylabel("Objective")
my_plt.export(plt.figure(2), fname="iter_obj_vals_singlegains")

#%%

all_cons = list(driver_cases[0].get_constraints().keys())
exp = "defects:(.*)"
cons = []
for i,c in enumerate(all_cons):
    match = re.search(exp, c)
    if match:
        name = match.group(1)
        name = name.replace("_", "\_")
        cons.append((c,name))

plt.figure(2)
for c,n in cons:
    var_data = np.zeros((len(iters),))
    for j, case in enumerate(driver_cases):
        var_data[j] = np.linalg.norm(case[c])
    
    plt.plot(iters, var_data, label=n, alpha=0.5)

plt.xlabel("Iteration")
plt.ylabel("Constraint Value")
plt.legend()

my_plt.export(plt.figure(2), fname="iter_constraint_vals_singlegains")
