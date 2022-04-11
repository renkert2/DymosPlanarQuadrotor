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

def subplots(prob=None, sim=None, path='traj.phase0.timeseries', vars=[], labels=[], legend=[], title="", save=False, axes=None, fig=None, simplot_kwargs={}, probplot_kwargs={}):
    if axes is None:
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
                l, = axes[i].plot(t_sim, s.get_val(f'{path}.{var}'), '-', **simplot_kwargs)
                lines.append(l)
                
                axes[i].axvline(x=t_sim[-1], linestyle="--", linewidth=l.get_linewidth()/2, color=l.get_color())
            if p:
                l, = axes[i].plot(t_prob, p.get_val(f'{path}.{var}'), 'o', **probplot_kwargs)
                lines.append(l)
                
                if not s:
                    axes[i].axvline(x=t_sim[-1], linestyle="--", linewidth=l.linewidth/2, color=l.color)
            
            if labels:
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

def timeseries_plots(sim_cases, title="Optimization", legend=["Initial", "Final"], show_plts=range(4)):    
    shared_args = [None, sim_cases]
    shared_kwargs = {"path":'traj.phase0.timeseries', "save":False, "legend":legend}
    
    v = [[] for i in range(4)]
    v[0] = [f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']]
    v[1] = ["states:PT_x1", "outputs:PT_a1", "outputs:PT_a2"]
    v[2] = ["outputs:PT_a3", "outputs:PT_a5"]
    v[3] = [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']]
    
    l = [[] for i in range(4)]
    l[0] = ['$x$', '$y$', r'$\theta$']
    l[1] = ["SOC", "Bus Voltage", "Battery Current (A)"]
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
    
def boundaryiterplots(b, reader):
    (fig, ax) = b.plot_boundary_2D()
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

