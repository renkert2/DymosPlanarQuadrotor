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

init.init_output(__file__)

name = "nominal_sim_cases"

reader = om.CaseReader(name+".sql")
cases = reader.get_cases("problem")

#%% 
print(reader.list_cases())

#%% Trajectory Comparisons
(fig, axes) = plotting.subplots(None, cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']],
                                labels=['$x$', '$y$', r'$\theta$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phase0.timeseries', save=False, 
                                vars=[f"controls:{x}" for x in  ['CTRL_x_T', 'CTRL_y_T', "CTRL_x_T_dot", "CTRL_y_T_dot"]],
                                labels=['$x_T$', '$y_T$', "$\dot{x}_T$", "$\dot{y}_T$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_u_1', 'CTRL_u_2'],
                                labels=['$u_1$', '$u_2$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_F_star_x', 'CTRL_F_star_y', 'CTRL_T_star'],
                                labels=['$F^*_x$', '$F^*_y$', "$T^*$"], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_theta_star', 'CTRL_tau_z_star'],
                                labels=['$\theta^*$', '$\tau^*_z$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])
#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_omega_1_star', 'CTRL_omega_2_star', "states:PT_x2", "states:PT_x3"],
                                labels=['$\omega^*_1$', '$\omega^*_2$', '$\omega_1$', '$\omega_2$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])

#%%
(fig, axes) = plotting.subplots(None, cases, path='traj.phases.phase0.timeseries', save=False, 
                                vars=['CTRL_e_omega_1', 'CTRL_e_omega_2'],
                                labels=[r'$e_{\omega_1}$', r'$e_{\omega_2}$'], 
                                title="Planar Quadrotor Input Optimization", 
                                legend=["Initial", "Final"])