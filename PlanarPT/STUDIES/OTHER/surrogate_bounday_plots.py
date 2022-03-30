# -*- coding: utf-8 -*-

import PlanarSystem as PS
import SUPPORT_FUNCTIONS.init as init
import my_plt
import matplotlib.pyplot as plt

p = PS.PlanarSystemParams()
s = PS.PlanarSystemSurrogates(p)
s.setup()


#%% Boundary Plots
figs = s.plot_boundary_3D()
names = [x+"_surrogate_boundary_plot" for x in s.surrogates.keys()]
for (fig,name) in zip(figs, names):
    my_plt.export(fig, fname = name)

plt.show()
