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
from DymosModel import _CalcF
from DymosModel import _CalcG

dm = DymosModel()
dm.ImportModel("PlanarPowerTrainModel")

nn = 10
cf = _CalcF(num_nodes = nn, _Calc = dm.Calc["f"], _CalcJ = dm.CalcJ["f"], _Metadata = dm.Metadata)
cg = _CalcG(num_nodes = nn, _Calc = dm.Calc["g"], _CalcJ = dm.CalcJ["g"], _Metadata = dm.Metadata)

p = om.Problem(model=om.Group())

ivc = om.IndepVarComp()
 ### INPUTS ###
 # x
meta = cf.options["_Metadata"]
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
p.model.add_subsystem('calcf', cf, promotes = ["*"])
p.model.add_subsystem('calcg', cg, promotes = ["*"])

p.setup()
p.run_model()

#%%