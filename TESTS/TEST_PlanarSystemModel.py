# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 07:30:25 2021

@author: renkert2
"""
import os
import openmdao.api as om
os.chdir(os.path.join(os.path.dirname(__file__), '..'))
from PlanarSystem import PlanarSystemModel
from PlanarBody.PlanarQuadrotorODE import PlanarQuadrotorODE 
from PlanarPT.PlanarPTModel import PlanarPTModel 

#%%
nn = 20
pt = PlanarPTModel(num_nodes=nn)

bm = PlanarQuadrotorODE(num_nodes=nn)


#%%
psm = PlanarSystemModel(num_nodes=20)


prob = om.Problem()
prob.model = psm;
prob.setup()
prob.run_model()