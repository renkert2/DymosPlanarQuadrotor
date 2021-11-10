# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 13:39:06 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import matplotlib.pyplot as plt

cr_without_plant_vars = om.CaseReader('without_plant_vars.sql')
cr_with_plant_vars = om.CaseReader('with_plant_vars.sql')

case_without_plant_vars = cr_without_plant_vars.get_case('final')
case_with_plant_vars = cr_with_plant_vars.get_case('final')

driver_with_plant_vars = cr_with_plant_vars.get_cases('driver', recurse=False)

# Plot Design Variables
r_vals = []
rho_vals = []
for case in driver_with_plant_vars:
    r_vals.append(case['r'])
    rho_vals.append(case['rho'])

iters = np.arange(len(r_vals))
fig, (ax1,ax2) = plt.subplots(2,1)

ax1.plot(iters, np.array(r_vals))
ax1.set(xlabel='Iterations', ylabel="Design Var: r", title="Optimization History")

ax2.plot(iters, np.array(rho_vals))
ax2.set(xlabel='Iterations', ylabel="Design Var: rho", title="Optimization History")
