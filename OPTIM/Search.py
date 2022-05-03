# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:46:59 2022

@author: renkert2
"""
import numpy as np
import Param as P
import itertools

import my_plt
import matplotlib.pyplot as plt
import matplotlib

import SUPPORT_FUNCTIONS.init
import Surrogate

class Search:
    def __init__(surrogates = None):
        self.search_surrogates = None # SearchSurrogates, Dictionary
        
        self.target = None # ParamValSet
        
        self.prob = None # OpenMDAO Problem used to evaluate feasibility and objectives
        # TODO: We may want to separate this out into multiple problems to reduce total overhead.  We could have separate problems for 1) evaluating configuration feasibility and configuration distance metric and 2) evaluating final dynamic objective
                    
class ConfigurationSearcher:
    def __init__(self, component_searchers, configuration_template=None):
        self.component_searchers = component_searchers # Dictionary of component searchers, key's are the "name" of the searcher
        
        # Configuration Template: specifies a complete component set, e.x.
        # configuration_template = ["Battery", "PMSMMotor", "Propeller"]
        # Entries correspond to keys of component_searchers
        if not configuration_template:
            configuration_template = list(component_searchers.keys())
        self.configuration_template =configuration_template
        
        self._sorted_sets_distances = None
        
    @property
    def sorted_sets(self):
        return [Surrogate.ComponentDataSet([cd[0] for cd in sd[0]]) for sd in self._sorted_sets_distances]
        
    @property
    def component_distances(self):
        return [[cd[1] for cd in sd[0]] for sd in self._sorted_sets_distances]
    
    @property
    def confiuration_distances(self):
        return [sd[1] for sd in self._sorted_sets_distances]
    
    def run(self):
        for searcher in self.component_searchers.values():
            searcher.run()
        self.sortSets()
        
    def enumerator(self):
        # Enumerates all possible sets from component_searchers' sorted comps corresponding to the configuration template
        cd_all = [self.component_searchers[name]._sorted_comps_distances for name in self.configuration_template]
        
        #TODO: We could think about this in a smarter way to that the enumerator considers component distances
        # as it builds the set to take some of the burden off the sort. 
        combinations = [c for c in itertools.product(*cd_all)]
        
        return combinations
    
    def configuration_distance(self, configs):
        # config_dist: list of (comp, distance) tuples
        comp_distances = [x[1] for x in configs]
        return np.linalg.norm(comp_distances)
        
    def sortSets(self):
        # Generates ComponentSets in ascending order of configuration distance
        sorted_sets = []
        combinations = self.enumerator()
        for s in combinations:
            d_s = self.configuration_distance(s)
            sorted_sets.append((s, d_s))
        
        sorted_sets.sort(key=lambda x : x[1])
        self._sorted_sets_distances = sorted_sets
        
        return sorted_sets
    
    def plotDistances(self, fig=None, ax=None, annotate=True):
        if not fig:
            fig = plt.figure()
        if not ax:
            ax = plt.axes()
            
        ax.plot(self.confiuration_distances, '-k', linewidth=2, label="$d_s$")
        
        comp_distances = self.component_distances
        for (i,name) in enumerate(self.configuration_template):
            d = [x[i] for x in comp_distances] # Get distance corresponding to individual component
            ax.plot(d, linewidth=1, alpha=0.4, label=f"$d_c$: {name}")
        
        ax.legend()
        ax.set_xlabel("Configuration")
        ax.set_ylabel("Distances")
        
        return (fig, ax)

class ComponentSearcher:
    # ComponentData Wrapper Class for Discrete Search
    def __init__(self, surrogate):
        self.boundary = surrogate.boundary
        self.comp_name = surrogate.comp_name
        self.comp_data = surrogate.comp_data
        
        self.target = None
        self.sorted_comps = None
        self._sorted_comps_distances = None

    def set_target(self, pv_target):
        self.target = P.ParamValSet([pv for pv in pv_target if pv.component == self.comp_name])
        
    def run(self):
        self.filterNearest()

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
        self._sorted_comps_distances = cd_dist
        self.sorted_comps = [x[0] for x in cd_dist]
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
        
            
        
    
    
    
    
        
        
        