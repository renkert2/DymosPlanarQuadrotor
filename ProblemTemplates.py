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

class StepProblem(om.Problem):
    def __init__(self):
        # Set up Desired Final Location:
        x_init=0
        y_init=0    
        
        x_des = 10
        y_des = 10
        
        def pos_margin(p, margin):
            # Takes a list of positions and returns the min and the max with a padded boundary
            p_max = max(p)
            p_min = min(p)
            d = margin*(p_max - p_min)
            return (p_min - d, p_max + d)
        
        (x_lb, x_ub) = pos_margin([x_init, x_des], 0.1)
        (y_lb, y_ub) = pos_margin([y_init, y_des], 0.1)
        
        nn = 20
        tx = dm.GaussLobatto(num_segments=nn)
        phase = ps.PlanarSystemDynamicPhase(transcription=tx)
        phase.init_vars()
        
        # Set up States and Inputs as Optimization Variables
        phase.set_time_options(fix_initial=True, initial_val=0, duration_bounds=(1, 20), duration_ref0=1, duration_ref=20)
        
        phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
        phase.set_state_options("PT_x2", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options("PT_x3", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options('BM_v_x', fix_initial=True, fix_final=True)
        phase.set_state_options('BM_v_y', fix_initial=True, fix_final=True)
        phase.set_state_options('BM_x', fix_initial=True, fix_final=True, lower=x_lb, ref0=x_lb, upper=x_ub, ref=x_ub)
        phase.set_state_options('BM_y', fix_initial=True, fix_final=True, lower=y_lb, ref0=y_lb, upper=y_ub, ref=y_ub)
        phase.set_state_options('BM_omega', fix_initial=True, fix_final=True)
        phase.set_state_options('BM_theta', fix_initial=True, fix_final=True, lower=-np.pi/2, ref0=-np.pi/2, upper=np.pi/2, ref=np.pi/2)
        
        phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
        phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
        
        phase.add_boundary_constraint('PT.x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
        phase.add_boundary_constraint('PT.x3_dot', loc='final', shape=(1,), equals=0)
        phase.add_boundary_constraint('BM.v_y_dot', loc='final', shape=(1,), equals=0)
        phase.add_boundary_constraint('BM.omega_dot', loc='final', shape=(1,), equals=0)
        
        # Minimize time at the end of the phase
        phase.add_objective('time', loc='final')
        
        traj = ps.PlanarSystemDynamicTraj(phase)
        traj.init_vars()
        
        planar_model=ps.PlanarSystemModel(traj)
        
        super().__init__(model=planar_model)
        
        self.driver = om.ScipyOptimizeDriver()
    
    def init_vals(self):
        # Set Initial Values
        self.set_val('traj.phase0.t_initial', 0.0)
        self.set_val('traj.phase0.t_duration', 10.0)
        
        self.set_val('traj.phase0.controls:PT_u1', 0.5)
        self.set_val('traj.phase0.controls:PT_u2', 0.5)
        
        self.set_val('traj.phase0.states:PT_x1', 1.0)
        
        phase = list(self.model.traj._phases.values())[0]
        self.set_val('traj.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
        self.set_val('traj.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
        self.set_val('traj.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
        self.set_val('traj.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
        self.set_val('traj.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 10]))
        self.set_val('traj.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 10]))
        self.set_val('traj.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
        self.set_val('traj.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))