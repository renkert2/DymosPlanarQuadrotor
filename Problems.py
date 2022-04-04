# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:39:09 2022

@author: renkert2
"""

import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import numpy as np
import Recorders
import Trajectories

class Problem(om.Problem):
    def __init__(self, planar_traj = None, model = None, **kwargs):
        super().__init__(model=model, **kwargs)
        self.planar_traj = planar_traj
        self.driver = om.ScipyOptimizeDriver()
        
    def setup(self):
        super().setup()
        
    def init_vals(self):
        self.planar_traj.init_vals(self)
        
    def list_problem_vars(self):
        super().list_problem_vars(desvar_opts=['lower', 'upper', 'ref', 'ref0'],
                       cons_opts=['lower', 'upper', 'ref', 'ref0'],
                       objs_opts=['ref', 'ref0'])        

 
def ForwardSimulation():
    nn = 20
    tx = dm.GaussLobatto(num_segments=nn, solve_segments='forward')
    phase = ps.PlanarSystemDynamicPhase(transcription=tx)
    phase.init_vars()
    
    # Setup Dynamic Problem
    phase.set_time_options(fix_initial=True, fix_duration=True, initial_val=0, duration_val=5)
    
    phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
    phase.set_state_options("PT_x2", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
    phase.set_state_options("PT_x3", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
    phase.set_state_options('BM_v_x', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_v_y', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_x', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_y', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_omega', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_theta', fix_initial=True, fix_final=False)
    
    phase.set_control_options("PT_u1", val=1, opt=False)
    phase.set_control_options("PT_u2", val=1, opt=False)
    
    traj = ps.PlanarSystemDynamicTraj(phase)
    traj.init_vars()
    
    planar_model=ps.PlanarSystemModel(traj)

    prob = om.Problem(model=planar_model)
    prob.driver = om.ScipyOptimizeDriver()
    prob.model.linear_solver = om.DirectSolver()
    
    prob.setup()

    # Set Initial Values
    prob.set_val('traj.phase0.t_initial', 0.0)
    prob.set_val('traj.phase0.t_duration', 5.0)
    
    prob.set_val('traj.phase0.controls:PT_u1', 1)
    prob.set_val('traj.phase0.controls:PT_u2', 1)
    
    prob.set_val('traj.phase0.states:PT_x1', 1.0)
    prob.set_val('traj.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
    prob.set_val('traj.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
    prob.set_val('traj.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
    prob.set_val('traj.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
    prob.set_val('traj.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 10]))
    prob.set_val('traj.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 10]))
    prob.set_val('traj.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
    prob.set_val('traj.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))
    
    return prob