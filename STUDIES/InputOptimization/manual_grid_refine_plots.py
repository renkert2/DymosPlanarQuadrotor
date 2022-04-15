# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 10:58:38 2022

@author: renkert2
"""
import my_plt
import matplotlib.pyplot as plt
import numpy as np
import SUPPORT_FUNCTIONS.init as init
import os
init.init_output(__file__)

num_segments = np.arange(10,40,5)
fevals = np.array([45,64,93,119,128,127])
time = np.array([2.873, 2.819, 2.796, 2.774, 2.775, 2.772])

(fig, axes) = plt.subplots(2,1)


fig.suptitle("Grid Refinement Test\n Gauss Lobatto Transcription; Compressed")

axes[0].plot(num_segments, fevals)
axes[0].set_xlabel("Number of Segments")
axes[0].set_ylabel("Function Evaluations")


axes[1].plot(num_segments, time)
axes[1].set_xlabel("Number of Segments")
axes[1].set_ylabel("Final Time (s)")

for ax in axes:
    ax.axvline(x = 25, linestyle='--', color='r')

my_plt.export(fig, fname="manual_grid_refine", directory=os.getcwd())
plt.show()