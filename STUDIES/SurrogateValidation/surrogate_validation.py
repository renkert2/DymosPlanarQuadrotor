# -*- coding: utf-8 -*-
"""
Created on Thu Jun 30 15:36:51 2022

@author: renkert2
"""

#%%
import os
import time
import dymos as dm
import openmdao.api as om
import numpy as np

import SUPPORT_FUNCTIONS.init as init
import PlanarSystem as PS
import Param as P

init.init_output(__file__)

ps = PS.PlanarSystemParams()
psurr = PS.PlanarSystemSurrogates(params=ps)

# Setup the Surrogates
psurr.setup()
        
### Build the Model ###
# Attach the surrogate fits
for (n,s) in psurr.items():
    s.fits.attach_outputs()
    
s = psurr.surrogates["Propeller"]
ps_s = P.ParamSet([*s.inputs, *s.outputs])
pg = P.ParamGroup(param_set = ps_s)
prob = om.Problem(model=pg)
prob.setup()
prob.run_model()

print(ps_s)
om.n2(prob, outfile="n2_sParams.html")

cd = s.comp_data[-10]
pv = cd.data

for p in s.inputs:
    p.load_val(pv)
    
print(ps_s)

prob.run_model()

print(ps_s)