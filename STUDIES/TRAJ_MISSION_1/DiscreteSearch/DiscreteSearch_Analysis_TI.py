# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search
import matplotlib.pyplot as plt
import numpy as np

import PlanarSystem as PS

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__, dirname="Output_20")
reader = search.SearchReader(output_dir = "search_output")

#%% Read Search Result
iters = reader.iterations
print(f"Number of Recorded Iterations: {len(iters)}")
for i in iters:
    print(f"Objective Function Value: {i.obj_val}")