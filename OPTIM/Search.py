# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:46:59 2022

@author: renkert2
"""
import numpy as np
import Param as P

import my_plt
import matplotlib.pyplot as plt
import matplotlib

class Search:
    def __init__(surrogates = None):
        self.search_surrogates = None # SearchSurrogates, Dictionary
        
        self.target = None # ParamValSet
        
        self.prob = None # OpenMDAO Problem used to evaluate feasibility and objectives
        # TODO: We may want to separate this out into multiple problems to reduce total overhead.  We could have separate problems for 1) evaluating configuration feasibility and configuration distance metric and 2) evaluating final dynamic objective
                    
class SearchSurrogate:
    # ComponentData Wrapper Class for Discrete Search
    def __init__(self, surrogate):
        self.boundary = surrogate.boundary
        self.comp_name = surrogate.comp_name
        self.comp_data = surrogate.comp_data
        
        self.target = None

    def set_target(self, pv_target):
        self.target = P.ParamValSet([pv for pv in pv_target if pv.component == self.comp_name])    

    def component_distance(self, candidate_comp, method="Norm", enforce_bounds=True):
        def param_error(t,c):
            # Parameter Error Calculation
            
            if method == "Norm":
                return ((c/t) - 1)
        
        def distance(param_errors):
            # Component Distance Metric
            return np.linalg.norm(param_errors)
        
        def check_valid(pv_t, pv_c):
            valid = True
            
            # Ensure candidate parameter is in bounds
            if enforce_bounds:
                if pv_t.lb and pv_c.val < pv_t.lb:
                    valid = False
                if pv_t.ub and pv_c.val > pv_t.ub:
                    valid = False
                
            return valid
        
        candidate = candidate_comp.data # Get ParamValSet from ComponentData
        errors = []
        for pv_t in self.target:
            pv_c = pv_t.get_compatible(candidate)
            if pv_c:
                valid = check_valid(pv_t, pv_c)
                if not valid:
                    # Exit function and return NaN distance
                    return None
                errors.append(param_error(pv_t.val, pv_c.val))
            
        return distance(errors)
        
    def filterNearest(self, **kwargs):        
        cd_dist = []
        for c in self.comp_data:
            d = self.component_distance(c, **kwargs)
            if d != None:
                cd_dist.append((c,d))
        
        cd_dist.sort(key = lambda x:x[1])
        return cd_dist
    
    def plotCompDistances(self, ax=None, fig=None, falloff_order = 1/10):
        (fig,ax) = self.boundary.plot2D(fig=fig,ax=ax)
        fig.suptitle(f"Component: {self.comp_name}")
        
        handles = []
        
        distances = []
        for c in self.comp_data:
            d = self.component_distance(c)
            if d:
                d = d**falloff_order
            distances.append(d)
        
        self.comp_data.plot(self.boundary.args, ax=ax, fig=fig, annotate=False, scatter_kwargs={"label":"Component Distance", "c":distances, "edgecolors":"0.8", "cmap":"Blues_r"})          
        
        for child in ax.get_children():
            if isinstance(child, matplotlib.collections.PathCollection):
                handles.append(child)
        
        
        
        # Add plot of Target:
        mkropts = {"marker":"o", "markersize":15, "markerfacecolor":"none", "markeredgewidth":2, "color":"k"}
        trgt_pnt = []
        for p in self.boundary.args:
            pv = p.get_compatible(self.target)
            trgt_pnt.append(pv.val)
        l_i, = ax.plot(*trgt_pnt, markeredgecolor="orange",  label="Target", **mkropts)
        handles.append(l_i)
        
        
        ax.legend(handles=handles)
        
        return (fig, ax)
        
            
        
    
    
    
    
        
        
        