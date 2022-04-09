# -*- coding: utf-8 -*-C:\Users\renkert2\Box\ARG_Research\Python\my_plt.py
"""
Created on Fri Jan 21 09:58:24 2022

@author: renkert2
"""
import os
from SUPPORT_FUNCTIONS.slugify import slugify
import matplotlib.pyplot as plt
import numpy as np
from . import init
import my_plt # loads style, provides export method

def subplots(prob=None, sim=None, path='traj.phase0.timeseries', vars=[], labels=[], legend=[], title="", save=False):
    fig, axes = plt.subplots(len(vars), 1)
    if not hasattr(axes, "__len__"):
        axes = (axes,)
        
    if prob:
        if not hasattr(prob, "__len__"):
            prob = (prob,)
        if not sim:
            sim = [None]*len(prob)
        else:
            if not len(sim) == len(prob):
                raise Exception("Prob and Sim Args must be the same length")
    
    if sim:
        if not hasattr(sim, "__len__"):
            sim = (sim,)
        if not prob:
            prob = [None]*len(sim)
        else:
            if not len(sim) == len(prob):
                raise Exception("Prob and Sim Args must be the same length")         
    
    for (j, (p,s)) in enumerate(zip(prob, sim)):
        if s:
            t_sim = s.get_val(f'{path}.time')
        if p:
            t_prob = p.get_val(f'{path}.time')
            
        for i, var in enumerate(vars):
            lines = []
            if s:
                l, = axes[i].plot(t_sim, s.get_val(f'{path}.{var}'), '-')
                lines.append(l)
            if p:
                l, = axes[i].plot(t_prob, p.get_val(f'{path}.{var}'), 'o')
                lines.append(l)
            
            axes[i].set_ylabel(labels[i])
            
            if legend:
                lines[0].set_label(legend[j])
    
    if legend:
        axes[0].legend() 
    
    axes[-1].set_xlabel('time (s)')
    plt.tight_layout()
    
    if title:
        fig.suptitle(r"\textbf{"+title+"}")
        if save:
            name = slugify(title)
            plt.savefig(f'{name}.png')
    
    return fig, axes

def timeseries_plots(sim_cases, title="Optimization"):
    graphics = []
    
    # Body States
    g = subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                    vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']],
                                    labels=['$x$', '$y$', r'$\theta$'], 
                                    title=f"{title}: Body States", 
                                    legend=["Initial", "Final"])
    graphics.append(g)
    
    # PT States
    v = ["states:PT_x1", "outputs:PT_a1", "outputs:PT_a2"]
    labels = ["SOC", "Bus Voltage", "Battery Current (A)"]
    g = subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                    vars=v,
                                    labels=labels, 
                                    title=f"{title}: Powertrain States ", 
                                    legend=["Initial", "Final"])
    graphics.append(g)
    
    
    v = ["outputs:PT_a3", "outputs:PT_a5"]
    labels = ["Inverter 1 Current (A)", "Inverter 2 Current (A)"]
    g = subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                    vars=v,
                                    labels=labels, 
                                    title=f"{title}: Inverter Currents", 
                                    legend=["Initial", "Final"])
    graphics.append(g)
    
    v = [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']]
    labels = ["Inverter 1 Input", "Inverter 2 Input"]
    g = subplots(None, sim_cases, path='traj.phase0.timeseries', save=False, 
                                    vars=v,
                                    labels=labels, 
                                    title=f"{title}: Inverter Inputs", 
                                    legend=["Initial", "Final"])
    graphics.append(g)
    return graphics
    
    

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

