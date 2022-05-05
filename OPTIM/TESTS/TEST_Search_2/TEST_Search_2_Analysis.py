# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search

init.init_output(__file__)

reader = search.SearchReader(output_dir = "search_output")

#%% Read problem cases
prob_cases = reader.problem_cases
    
#%% Read Iterations
iters = reader.iterations

#%% Read Search Result
result = reader.result
    
    