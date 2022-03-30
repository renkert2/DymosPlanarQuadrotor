# -*- coding: utf-8 -*-C:\Users\renkert2\Box\ARG_Research\Python\my_plt.py
"""
Created on Fri Jan 21 09:58:24 2022

@author: renkert2
"""
import os
from SUPPORT_FUNCTIONS.slugify import slugify
import matplotlib.pyplot as plt
import numpy as np
import init
import my_plt # loads style, provides export method

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
    
def iterplots(case_reader, vars, labels=[], title="", save=False, **kwargs):
    # Get driver cases (do not recurse to system/solver cases)
    driver_cases = case_reader.get_cases('driver', recurse=False)
    
    fig, axes = plt.subplots(len(vars), 1, **kwargs)
    if len(vars) == 1:
        axes = (axes,)
    
    iters = np.arange(len(driver_cases))
    
    for i, var in enumerate(vars):
        var_data = np.zeros((len(iters),))
        for j, case in enumerate(driver_cases):
            var_data[j] = case[var]
        axes[i].plot(iters, var_data)
        if labels:
            axes[i].set_ylabel(labels[i])
    axes[-1].set_xlabel('Iteration')
    plt.tight_layout()
    if title:
        fig.suptitle(r"\textbf{"+title+"}")
        if save:
            name = slugify(title)
            plt.savefig(f'{name}.png')
    plt.show()

