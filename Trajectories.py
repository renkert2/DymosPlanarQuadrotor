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
     
     def __init__(self):
         self.traj = None # PlanarSystemDynamicTraj, Used to construct System Model
         self.tx = None # Problem transcription
         self.nn = None # 
         
         self.driver = None # Baseline driver to solve the optimal control problem
         self.prob = None  # Used for solving the optimal control problem, requires ParameterSystem for initialization of variables
     
     def setup(self):
         pass
     
     def init_vals(self, prob):
         pass
     
     def refine(self, **kwargs):
         self.prob.final_setup()
         failed = _refine_iter(self.prob, **kwargs)
         return self.prob.model.traj
         