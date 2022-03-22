# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import ProblemTemplates as PT
import numpy as np

init.init_output(__file__)

prob = PT.StepProblem()

# Make the Frame Mass Independent
params = prob.model.params._params
params["Mass__Frame"].dep = False

prob.setup()
prob.init_vals()

# Parameter Values
prob.set_val('params.Mass__Frame', 1)

print("Running Model")
prob.run_model()

om.n2(prob)

#%%
# Run the Optimization Problem for Various Masses
mass_vals = np.arange(0.05, 1.05, 0.1)

for val in mass_vals:
    prob.set_val('params.Mass__Frame', val)
    print(f"Solving optimization for mass {val}")
    prob.run_driver(case_prefix=f"MassVal_{val}")
    prob.record(f"MassVal_{val}")
    final_time = prob.get_val('traj.phase0.t_duration')
    print(f"Final time: {final_time}")





    
