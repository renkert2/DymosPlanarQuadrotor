# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 15:22:21 2022

@author: renkert2
"""

import openmdao.api as om
import os
os.chdir(os.path.join(os.path.dirname(__name__), ".."))
import PlanarSystem as ps
import SUPPORT_FUNCTIONS.plotting
import matplotlib.pyplot as plt
import numpy as np


model = ps.PlanarSystemStaticModel(IncludeBody=False, SolveMode="Forward")

prob = om.Problem(model=model)

prob.setup()
prob.model.list_inputs(prom_name=True)
prob.model.list_outputs(prom_name=True)
#%%
### Input Test
# Run the model for a range of inputs from 0 to 1
input_vector = np.arange(0,1,0.05)
data_list = []
for input in input_vector:
    prob.set_val("PT.u1", input)
    prob.run_model()
    data = prob.get_val("PT.y1")
    print("Input is: ", input)
    print("Thrust is: ", data)
    data_list.append(data.copy())
    
prob.set_val("PT.u1", 1.0)
prob.run_model()

print("Max Thrust is: ", prob.get_val("PT.y1"))

#%%
plt.plot(input_vector, data_list)
plt.xlabel('Input')
plt.ylabel('Thrust (N)')
plt.show()