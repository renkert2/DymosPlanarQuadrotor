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

p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()


#%% Boundary Plots

#s.plot_boundary_3D()

#%% Setup()
c = s["Propeller"].boundary