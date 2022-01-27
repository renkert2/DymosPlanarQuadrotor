# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 09:58:24 2022

@author: renkert2
"""
import os
from SUPPORT_FUNCTIONS.slugify import slugify
import matplotlib.pyplot as plt

mtlb = os.getenv('MYPYTHON')
plt.style.use(os.path.join(mtlb, 'research_default.mplstyle'))

def subplots(sim, prob, path='traj.phase0.timeseries', vars=[], labels=[], title="", save=False):
    if sim:
        t_sim = sim.get_val(f'{path}.time')
    if prob:
        t_prob = prob.get_val(f'{path}.time')
        
    
    fig, axes = plt.subplots(len(vars), 1)
    for i, var in enumerate(vars):
        if sim:
            axes[i].plot(t_sim, sim.get_val(f'{path}.{var}'), '-')
        if prob:
            axes[i].plot(t_prob, prob.get_val(f'{path}.{var}'), 'o')
        axes[i].set_ylabel(labels[i])
    axes[-1].set_xlabel('time (s)')
    plt.tight_layout()
    if title:
        fig.suptitle(r"\textbf{"+title+"}")
        if save:
            name = slugify(title)
            plt.savefig(f'{name}.png')
    plt.show()