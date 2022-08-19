# -*- coding: utf-8 -*-
"""
Created on Mon May 16 15:07:10 2022

@author: renkert2
"""

import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import IndexSurrogate as IS
from GraphTools_Phil_V2.OpenMDAO import Param as P

init.init_output(__file__)

p = P.Param(name="y", strID="y", val=10) 
pc = IS.IndexParamComp(set_vals=[1,2,3,4,5])
p.setDependency(pc)

p2 = P.Param(name='z', strID = "z", val=20)
pc2 = IS.IndexParamComp(set_vals=[10,20,30,40,50])
p2.setDependency(pc2)

p3 = P.Param(name="w", strID = "w")
pc3 = P.ParamComp(om.AddSubtractComp, output_name="w", input_names=("y", "z"))
p3.setDependency(pc3, {"y":p, "z":p2})

ps = P.ParamSet([p, p2, p3])


#%%
g = P.ParamGroup(param_set = ps)
s = P.ParamSystem(g)
prob = om.Problem(model=s)
prob.setup()

#%%
om.n2(prob)