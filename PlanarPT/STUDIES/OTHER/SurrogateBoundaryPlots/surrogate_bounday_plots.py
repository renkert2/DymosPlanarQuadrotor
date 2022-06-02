# -*- coding: utf-8 -*-

import PlanarSystem as PS
import SUPPORT_FUNCTIONS.init as init
import my_plt
import matplotlib.pyplot as plt
import os

init.init_output(__file__)

p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()


#%% Boundary Plots
figs = s.plot_boundary_3D()
names = [x+"_surrogate_boundary_plot" for x in s.surrogates.keys()]

d = os.path.join(os.path.dirname(__file__), "Output")
for (graphics,name) in zip(figs, names):
    fig = graphics[0]
    my_plt.export(fig, fname = name, directory=d)

plt.show()
