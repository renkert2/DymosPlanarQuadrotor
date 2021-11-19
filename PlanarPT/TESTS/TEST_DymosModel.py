# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 11:14:36 2021

@author: renkert2
"""
import sys
import os
import openmdao.api as om
os.chdir('..')
sys.path.append(r'C:\Users\renkert2\Documents\ARG_Research\GraphTools\Dymos')
from DymosModel import DymosModel



nn = 10

p = om.Problem(model = om.Group())
mdl = "PlanarPowerTrainModel"
dm = DymosModel(num_nodes = nn, Model = mdl)
dm.ImportModel(mdl)

ivc = om.IndepVarComp()
 ### INPUTS ###
 # x
meta = dm.Metadata
state_table = meta["StateTable"]
for var in state_table:
     ivc.add_output(var["StateVariable"], val=1, shape=(nn,))
     
 # u
input_table = meta["InputTable"]
for var in input_table:
     ivc.add_output(var["InputVariable"], val=1, shape=(nn,))
 
 # d
disturbance_table = meta["DisturbanceTable"]
for var in disturbance_table:
     ivc.add_output(var["DisturbanceVariable"], val=1, shape=(nn,))
     
 # theta
param_table = meta["ParamTable"]
for param in param_table:
     ivc.add_output(param["SymID"], val=param["Value"], tags=['dymos.static_target'])
 
p.model.add_subsystem('vars', ivc, promotes = ["*"])
p.model.add_subsystem('dm', dm, promotes = ["*"])

p.setup(force_alloc_complex=True)
p.run_model()
cpd = p.check_partials(method='cs', compact_print=True)

#%%