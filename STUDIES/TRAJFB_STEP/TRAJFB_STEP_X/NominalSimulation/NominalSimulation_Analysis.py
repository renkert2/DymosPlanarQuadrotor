#%%
import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os

init.init_output(__file__)

name = "nominal_sim_cases"
simname = "nominal_sim_cases_sim"

reader = om.CaseReader(name+".sql")
cases = reader.get_cases("problem")

sim_reader = om.CaseReader(simname+".sql")
sim_cases = sim_reader.get_cases("problem")

#%% 
print(reader.list_cases())

#%% Trajectory Comparisons
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']],
                                labels=['$x$', '$y$', r'$\theta$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(cases, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"controls:{x}" for x in  ['CTRL_x_T', 'CTRL_y_T', "CTRL_v_x_T", "CTRL_v_y_T"]],
                                labels=['$x_T$', '$y_T$', "$\dot{x}_T$", "$\dot{y}_T$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_u_1', 'CTRL_u_2'],
                                labels=['$u_1$', '$u_2$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_F_star_x', 'CTRL_F_star_y', 'CTRL_T_star'],
                                labels=['$F^*_x$', '$F^*_y$', "$T^*$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
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
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
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

#%% Position Reference Following
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']],
                                labels=['$x$', '$y$', r'$\theta$'], 
                                title="Position Reference Following", 
                                legend=["Final"])
(f, axes) = plotting.subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, axes=axes,
                                vars=['controls:CTRL_x_T', 'controls:CTRL_y_T', "CTRL_theta_star"])

for ax in axes:
    ax.legend(["State",None, "Reference",None])

my_plt.export(fig, "step_x_position_stable")

#%% Rotor Speed Reference Following
(fig, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=["states:PT_x2", "states:PT_x3"],
                                labels=['$\omega_1$', '$\omega_2$'], 
                                title="Speed Reference Following")
(f, axes) = plotting.subplots(None, sim_cases, path='traj.phases.phase0.timeseries', save=False, axes=axes,
                                vars=['CTRL_omega_1_star', 'CTRL_omega_2_star'])

for ax in axes:
    ax.legend(["State",None, "Reference",None])

my_plt.export(fig, "step_x_rotorspeed_stable")