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
from dymos.grid_refinement.refinement import _refine_iter

class PlanarTrajectory:
     # Superclass for specific optimal control trajectories that we want the vehicle to take.
     # We want all options, etc to be constant so that the trajectories are uniform across all problems
     
     def __init__(self, traj=None, tx=None, prob=None):
         self.traj = traj # PlanarSystemDynamicTraj, Used to construct System Model
         self.tx = tx # Problem transcription
         self.prob = prob # Used for solving the optimal control problem, requires ParameterSystem for initialization of variables
         
         self.setup()
         
     def setup(self):
         pass
         # Setup Problem

     def init_vals(self, prob):
         pass
     
     def refine(self, **kwargs):
         self.prob.final_setup()
         failed = _refine_iter(self.prob, **kwargs)
         return self.prob.model.traj
     

### Trajectories ###
class Step(PlanarTrajectory):
    def __init__(self, **kwargs):
        
        tx=dm.GaussLobatto(num_segments=20)
        self.x_init=0
        self.y_init=0    
        
        self.x_des = 10
        self.y_des = 10
        
        super().__init__(tx=tx)

    def setup(self):
        def pos_margin(p, margin):
            # Takes a list of positions and returns the min and the max with a padded boundary
            p_max = max(p)
            p_min = min(p)
            d = margin*(p_max - p_min)
            return (p_min - d, p_max + d)
        
        (self.x_lb, self.x_ub) = pos_margin([self.x_init, self.x_des], 0.1)
        (self.y_lb, self.y_ub) = pos_margin([self.y_init, self.y_des], 0.1)

        phase = ps.PlanarSystemDynamicPhase(transcription=self.tx)
        phase.init_vars()
        
        # Set up States and Inputs as Optimization Variables
        phase.set_time_options(fix_initial=True, initial_val=0, duration_bounds=(1, 20), duration_ref0=1, duration_ref=20)
        
        phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
        phase.set_state_options("PT_x2", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options("PT_x3", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options('BM_v_x', fix_initial=True, fix_final=True)
        phase.set_state_options('BM_v_y', fix_initial=True, fix_final=True)
        phase.set_state_options('BM_x', fix_initial=True, fix_final=True, lower=self.x_lb, ref0=self.x_lb, upper=self.x_ub, ref=self.x_ub)
        phase.set_state_options('BM_y', fix_initial=True, fix_final=True, lower=self.y_lb, ref0=self.y_lb, upper=self.y_ub, ref=self.y_ub)
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
        
        self.traj = ps.PlanarSystemDynamicTraj(phase)
        self.traj.init_vars()
    
    def init_vals(self, prob, name="traj"):
        # Set Initial Values
        prob.set_val(f'{name}.phase0.t_initial', 0.0)
        prob.set_val(f'{name}.phase0.t_duration', 10.0)
        
        prob.set_val(f'{name}.phase0.controls:PT_u1', 0.5)
        prob.set_val(f'{name}.phase0.controls:PT_u2', 0.5)
        
        prob.set_val(f'{name}.phase0.states:PT_x1', 1.0)
        
        phase = list(self.traj._phases.values())[0]
        prob.set_val(f'{name}.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
        prob.set_val(f'{name}.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
        prob.set_val(f'{name}.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 10]))
        prob.set_val(f'{name}.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 10]))
        prob.set_val(f'{name}.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))
        
         