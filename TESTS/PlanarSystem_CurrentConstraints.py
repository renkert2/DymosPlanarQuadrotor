# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 15:46:01 2022

@author: renkert2
"""

import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np

import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.timing as timing
import Constraints as C
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps

init.init_output(__file__)

traj = T.Step()
traj.setup()

cons = C.ConstraintSet()
cons.add(C.BatteryCurrent())
model = ps.PlanarSystemModel(traj.traj, cons = cons)
prob = P.Problem(model=model, planar_traj = traj)

prob.setup()
prob.init_vals()

prob.run_driver()

prob.list_problem_vars()



