# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

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
import ProblemTemplates as PT
import Recorders as R

init.init_output(__file__)

prob_temp = PT.StepProblem

prob = prob_temp(model_kw={})
prob = R.SimpleRecorder(prob, name="init_cases.sql")
prob.setup()
prob.init_vals()
prob.final_setup()
prob.list_problem_vars()

# Run the Initial Optimization Problem
run_driver = timing.simple_timer(prob.run_driver)
#run_driver()
#prob.record('init')
prob.cleanup()

prob = prob_temp(model_kw={"opt_comps":{"Battery":["Q"]}})
prob = R.OptiRecorder(prob, name="opt_cases.sql")
prob.setup()
prob.init_vals()
prob.final_setup()
prob.list_problem_vars()

# Run the PlantDesign Optimization Problem
run_driver = timing.simple_timer(prob.run_driver)
run_driver()
prob.record('opt')
prob.cleanup()

# TODO: Run and save simulations
#