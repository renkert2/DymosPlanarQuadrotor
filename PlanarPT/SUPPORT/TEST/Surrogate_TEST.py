# -*- coding: utf-8 -*-

import os
import sys
home = "C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor"
if home not in  sys.path:
    sys.path.append(home)
import PlanarSystem as PS
import SUPPORT_FUNCTIONS.init as init
import openmdao.api as om
import matplotlib.pyplot as plt
import PlanarPT.SUPPORT.Surrogate as S
import Param as P

#%%
p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()

#%% ComponentData
cd_all = S.ComponentDataSet()
comb = S.ComponentDataSet()
for s_ in s.surrogates.values():
    cd_all.update(s_.comp_data)
    comb.add(s_.comp_data[0])
    
print(cd_all)
print(comb)

#%%
s.plot_boundary_2D()

#%% compatible params
p_D = p["P__Propeller"]


print(p_D.get_compatible(comb.data))

#%% Loading Params
print(p)
for p_ in p:
    p_.load_val(comb.data)