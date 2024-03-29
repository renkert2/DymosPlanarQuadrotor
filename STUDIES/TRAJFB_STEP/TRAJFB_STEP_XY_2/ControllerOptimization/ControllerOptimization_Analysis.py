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

init.init_output(__file__, "Output")

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
my_plt.export(fig, "step_xy_dynamicsconvergence_corr_inputratecon")

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"controls:{x}" for x in  ['CTRL_x_T', 'CTRL_y_T', "CTRL_v_x_T", "CTRL_v_y_T"]],
                                labels=['$x_T$', '$y_T$', "$\dot{x}_T$", "$\dot{y}_T$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
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
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_F_star_x', 'CTRL_F_star_y', 'CTRL_T_star'],
                                labels=['$F^*_x$', '$F^*_y$', "$T^*$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])
my_plt.export(fig, "step_xy_des_forces")
#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_theta_star', 'CTRL_tau_z_star'],
                                labels=['$\\theta^*$', '$\\tau^*_z$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['states:BM_omega'],
                                labels=['$\\omega$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=["states:PT_x2", "states:PT_x3"],
                                labels=['$\omega_1$', '$\omega_2$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial","Final"])

#my_plt.export(fig, "step_xy_rotorspeeds")
#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_omega_1_star', 'CTRL_omega_2_star', "states:PT_x2", "states:PT_x3"],
                                labels=['$\omega^*_1$', '$\omega^*_2$', '$\omega_1$', '$\omega_2$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial","Final"])

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


#my_plt.export(fig, "step_xy_referencetracking")


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

#%%
plt.figure(1)
var = 'params.k_d_r_x__Controller'
var_data = np.zeros((len(iters),))
for j, case in enumerate(driver_cases):
    var_data[j] = case[var][-1]
    
plt.plot(iters,var_data)
plt.xlabel("Iteration")
plt.ylabel("$k_{p,r}$")
#my_plt.export(plt.figure(1), fname="iter_desvar_vals_singlegain")

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

all_cons = list(cases[0].get_constraints().keys())
exp = "defects:(.*)"
cons = []
for i,c in enumerate(all_cons):
    match = re.search(exp, c)
    if match:
        name = match.group(1)
        name = name.replace("_", "\_")
        cons.append((c,name))

#%%
plt.figure(2)
for c,n in cons:
    var_data = np.zeros((len(iters),))
    for j, case in enumerate(driver_cases):
        var_data[j] = np.linalg.norm(case[c])
    
    plt.plot(iters, var_data, label=n, alpha=0.5)

plt.xlabel("Iteration")
plt.ylabel("Constraint Value")
plt.legend()

#my_plt.export(plt.figure(2), fname="iter_constraint_vals_singlegains")

#%%
plt.figure(1)
node_times = np.unique(cases[-1].get_val("traj.phases.phase0.time.time"))
col_node_times = node_times[1:-1:2]
plt.figure(1)
for c,n in cons:
    plt.plot(col_node_times, cases[-1][c], label=n)
plt.legend(loc="upper left")
plt.xlabel("Time (s)")
plt.ylabel("Constraint Value")

#my_plt.export(plt.figure(1), fname="defect_cons_all_corr_inputratecon")

#%% Compare to Controller Optimization Results
for var in ["k_p_r__Controller","k_d_r_x__Controller","k_d_r_y__Controller","k_p_theta__Controller","k_d_theta__Controller","k_p_omega__Controller","k_b_omega__Controller","k_i_omega__Controller"]:
    var = "traj.param_comp.parameter_vals:"+var
    print(f"Case Val: {cases[-1].get_val(var)}, Sim Val: {sim_cases[-1].get_val(var)}, error:{cases[-1].get_val(var) - sim_cases[-1].get_val(var)}")

