# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
import time
import SUPPORT_FUNCTIONS.init as init
import ProblemTemplates as PT

init.init_output(__file__)

prob = PT.StepProblem()

# Make the Frame Mass Independent
params = prob.model.params._params
params["Mass__Frame"].dep = False

prob.model.add_design_var('params.Mass__Frame', lower=0.1, upper=20, ref0=0.1, ref=20)
prob.model.add_constraint('thrust_ratio.TR', lower=1.5, upper=1.75, ref0=1.5, ref=1.75)

prob.setup()
prob.init_vals()

# Parameter Values
prob.set_val('params.Mass__Frame', 10)


#%%
# Run the Optimization Problem
tic = time.perf_counter()
prob.run_driver()
toc = time.perf_counter()
run_time = toc-tic
print(f"Problem solved in {run_time:0.4f} seconds")
prob.cleanup()

#%%
final_mass = prob.get_val("params.Mass__Frame")
final_tr = prob.get_val("thrust_ratio.TR")
print(f"Final Mass is {final_mass} with Thrust Ratio {final_tr}")
    
