# -*- coding: utf-8 -*-C:\Users\renkert2\Box\ARG_Research\Python\my_plt.py
"""
Created on Fri Jan 21 09:58:24 2022

@author: renkert2
"""
import os
from SUPPORT_FUNCTIONS.slugify import slugify
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from . import init
from ARG_Research_Python import my_plt # loads style, provides export method

def subplots(prob=None, sim=None, path=['traj.phase0.timeseries'], vars=[], labels=[], legend=[], title="", save=False, axes=None, fig=None, simplot_kwargs={}, probplot_kwargs={}, plot_dividers=True):
    if axes is None:
        fig, axes = plt.subplots(len(vars), 1)
    if not hasattr(axes, "__len__"):
        axes = (axes,)
        
    if not isinstance(path, (list, tuple)):
        path = [path]
        
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
                
    def _get_val(prob, paths, return_arrays=False):
        val_arrays = []
        for p in paths:
            val = prob.get_val(p)
            val_arrays.append(val)
        
        val_cat = np.concatenate(val_arrays)
        if return_arrays:
            return (val_cat, val_arrays)
        else:
            return val_cat 
    
    for (j, (p,s)) in enumerate(zip(prob, sim)):
        if s:
            t_sim, t_sim_arr = _get_val(s,[f'{p}.time' for p in path], return_arrays=True)
        if p:
            t_prob, t_prob_arr = _get_val(p,[f'{p}.time' for p in path], return_arrays=True)
            
        for i, var in enumerate(vars):
            lines = []
            if s:
                l, = axes[i].plot(t_sim, _get_val(s, [f'{p}.{var}' for p in path]), '-', **simplot_kwargs)
                lines.append(l)
                
                if plot_dividers:
                    for arr in t_sim_arr:
                        axes[i].axvline(x=arr[-1], linestyle="--", linewidth=l.get_linewidth()/2, color=l.get_color())
                
            if p:
                l, = axes[i].plot(t_prob, _get_val(p, [f'{p}.{var}' for p in path]), 'o', **probplot_kwargs)
                lines.append(l)
                
                if not s and plot_dividers:
                    for arr in t_prob_arr:
                        axes[i].axvline(x=arr[-1], linestyle="--", linewidth=l.get_linewidth()/2, color=l.get_color())
            
            if labels:
                axes[i].set_ylabel(labels[i])
            
            if legend:
                lines[0].set_label(legend[j])
    
    if legend:
        axes[0].legend() 
    
    axes[-1].set_xlabel('Time (s)')
    plt.tight_layout()
    
    if title:
        fig.suptitle(r"\textbf{"+title+"}")
        if save:
            name = slugify(title)
            plt.savefig(f'{name}.png')
    
    return fig, axes

def timeseries_plots(prob=None, sim=None, phases=['phase0'], title="Optimization", legend=["Initial", "Final"], show_plts=range(4)):    
    shared_args = [prob, sim]
    
    if not isinstance(phases, (list, tuple)):
        phases = [phases]
    
    paths = [f'traj.{p}.timeseries' for p in phases]
    shared_kwargs = {"path":paths, "save":False, "legend":legend}
    
    v = [[] for i in range(4)]
    v[0] = [f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']]
    v[1] = ["states:PT_x1", "outputs:PT_a1", "outputs:PT_a2"]
    v[2] = ["outputs:PT_a3", "outputs:PT_a5"]
    v[3] = [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']]
    
    l = [[] for i in range(4)]
    l[0] = ['$x$ (m)', '$y$ (m)', r'$\theta$ (rad)']
    l[1] = ["Battery SOC", "Bus Voltage (V)", "Bus Current (A)"]
    l[2] = ["Inverter 1 Current (A)", "Inverter 2 Current (A)"]
    l[3] =  ["Inverter 1 Input", "Inverter 2 Input"]
    
    t = ["Body States", "Powertrain States", "Inverter Currents", "Inverter Inputs"]
    
    graphics = []
    for i in show_plts:
        g = subplots(*shared_args, **shared_kwargs, vars=v[i], labels=l[i], title=f"{title}: {t[i]}")
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
    axes[-1].set_xlabel('Function Evaluations')
    plt.tight_layout()
    if title:
        fig.suptitle(r"\textbf{"+title+"}")
        if save:
            name = slugify(title)
            plt.savefig(f'{name}.png')
    plt.show()
    
    return (fig, axes)
    
def boundaryiterplots(b, reader):
    (fig, ax) = b.plot_boundary_2D()
    
    # Change scatterplot color
    scp = ax.findobj(match = matplotlib.collections.PathCollection)[0]
    scp.set_edgecolor('0.8')
    
    
    fig.suptitle(f"Design Space: {b.comp_name}")
    opt_vars = [f"params.{p.strID}" for p in b.boundary.args]
    (iters, vals) = reader.get_itervals(opt_vars)
    ax.plot(vals[0], vals[1], '.-k', markersize=10, linewidth=1)
    
    mkropts = {"marker":"o", "markersize":15, "markerfacecolor":"none", "markeredgewidth":2, "color":"k"}
    # Initial Point
    x_0 = [v[0] for v in vals]
    l_i, = ax.plot(*x_0, markeredgecolor="orange",  label="Initial", **mkropts)
    
    # Initial Point
    x_f = [v[-1] for v in vals]
    l_f, = ax.plot(*x_f, markeredgecolor="green",  label="Final", **mkropts)
    
    ax.legend(handles=[l_i, l_f])
    
    return (fig, ax, mkropts)

