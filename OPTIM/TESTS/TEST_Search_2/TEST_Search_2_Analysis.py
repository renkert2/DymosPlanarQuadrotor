# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search
import matplotlib.pyplot as plt

init.init_output(__file__)

reader = search.SearchReader(output_dir = "search_output")

#%% Read problem cases
case_reader = reader.case_reader
prob_cases = reader.problem_cases

print(case_reader.list_cases())
    
#%% Read Iterations
iters = reader.iterations

# Get Thrust Ratio of all iterations
for (i,iteration) in enumerate(iters):
    c = case_reader.get_case(iteration.case_name)
    tr = c.get_val("constraint__thrust_ratio.TR")
    print(f"Iteration {i}: thrust_ratio={tr}")

#%% Read Search Result
result = reader.result

print(result)
#print(result.base_case_data.input_data)
#print(result.base_case_data.output_data)

#%%
result.plot()
#%%
result.plotDesignSpace()