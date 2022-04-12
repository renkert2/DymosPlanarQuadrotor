# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:47:29 2022

@author: renkert2
"""

import openmdao.api as om
from openmdao.recorders.sqlite_reader import SqliteCaseReader
import os
import json
import numpy as np
from tabulate import tabulate
import fnmatch
from SUPPORT_FUNCTIONS import support_funcs

class Recorder:
    def __init__(self, recorder = None, sim_recorder=None, name='cases.sql'):
        name, ext = os.path.splitext(name)
        
        if not recorder:
            recorder = om.SqliteRecorder(name+ext, record_viewer_data=False)
        self.recorder = recorder
        
        if not sim_recorder:
            sim_recorder = om.SqliteRecorder(name+"_sim"+ext, record_viewer_data=False)
        self.sim_recorder = sim_recorder
        
        self.name = name
        self.prob = None
        self.driver = None
        self.sim_prob = None
        
    def add_prob(self, prob):
        prob.add_recorder(self.recorder)
        prob.recording_options['record_desvars'] = True
        prob.recording_options['record_responses'] = True
        prob.recording_options['record_objectives'] = True
        prob.recording_options['record_constraints'] = True
        prob.recording_options['record_inputs'] = True
        
        prob.recording_options["record_rel_error"] = True
        prob.recording_options["record_residuals"] = True
        
        prob.recording_options['includes'] = ["*"]
        
        self.prob = prob
        return prob
    
    def add_driver(self, driver):
        driver.add_recorder(self.recorder)
        driver.recording_options['excludes'] = ['traj.*']
        driver.recording_options['record_objectives'] = True
        driver.recording_options['record_constraints'] = True
        driver.recording_options['record_desvars'] = True
        driver.recording_options['record_inputs'] = True
        driver.recording_options['record_outputs'] = True
        driver.recording_options['record_residuals'] = False
        
        self.driver = driver
        return driver
    
    def add_sim_prob(self, sim_prob):        
        sim_prob.add_recorder(rec=self.sim_recorder)
        # can modify options here if we want with sim_prob.recording_options
        self.sim_prob = sim_prob
        
    def record_results(self):
        results = {}
        results["prob_recorder"] = self.recorder._filepath
        results["sim_recorder"] = self.sim_recorder._filepath
        results["name"] = self.name
        
                
        driver_results = dict(self.driver.result)
        for key in ["x", "jac"]:
            del driver_results[key]
        for k,v in driver_results.items():
            if hasattr(v, "tolist"): # Convert numpy arrays to json
                driver_results[k] = v.tolist()
        
        
        results["driver"] = driver_results
        
        cons = self.prob.model.cons
        results["cons"] = [con.props() for con in cons]
        
            
        def param_props(param):
            propnames = ["strID", "val", "dep", "opt", "x0", "lb", "ub"]
            d = {}
            for p in propnames:
                v = getattr(param, p)
                if hasattr(v, "tolist"): # Convert numpy arrays to json
                    v = v.tolist()
                d[p]=v
            return d
        params = self.prob.model._params
        results["params"] = [param_props(p) for p in params]
        
        with open(f'{self.name}_results.json', 'w') as fp:
            json.dump(results, fp, indent=4)
        
        return results

class Reader(SqliteCaseReader):
    def get_itervals(self, itervars):
        driver_cases = self.get_cases('driver', recurse=False)
        N = len(driver_cases)
        iters = np.arange(N)
        
        var_data = []
        for i, var in enumerate(itervars):
            vd = np.zeros((N,))
            for j, case in enumerate(driver_cases):
                vd[j] = case[var]
            var_data.append(vd)
        
        return iters, var_data
    
    def delta_table(self, init_case_name = None, final_case_name = None, includes = {"objectives":None, "design_vars":"params.*"}):
        prob_cases = self.get_cases("problem")
        if init_case_name:
            init_case = self.get_case(init_case_name)
        else:
            init_case = prob_cases[0]
            
        if final_case_name:
            final_case = self.get_case(final_case_name)
        else:
            final_case = prob_cases[-1]
            
        delta_dict = {}
        for c,n in zip((init_case, final_case), ("initial", "final")):
            for method, name in zip([c.get_objectives, c.get_design_vars, c.get_constraints], ["objectives", "design_vars", "constraints"]):
                if name in includes:
                    vals = method(scaled=False)
                    
                    # Filter with Includes
                    inc = includes[name]
                    if inc:
                        vals = {key:value for key,value in vals.items() if fnmatch.fnmatch(key, inc)}
                    
                    for key,val in vals.items():
                        val = support_funcs.scalarize(val)
                        d = {n:val}
                        if name not in delta_dict:
                            delta_dict[name] = {}
                        if key not in delta_dict[name]:
                            delta_dict[name][key] = {}
                        delta_dict[name][key].update(d)
                
        for d_outer in delta_dict.values():
            for d in d_outer.values():
                num = (d["final"] - d["initial"])
                den = abs(d["initial"])
                if hasattr(num, "__len__") or den != 0:
                    d["percent_change"] = num/den
                else:
                    d["percent_change"] = np.copysign(float('inf'), num)
                    
        # Make Summary Table
        latex_tables = {}
        header_dict = {" ":["Initial", "Final", "Rel. Change"]}
        for (name, val) in delta_dict.items():
            val_tab = {k:list(v.values()) for k,v in val.items()}
            val_tab = {**header_dict, **val_tab}
            t = tabulate(val_tab, headers="keys")
            print(t)
            
            t_latex = tabulate(val_tab, headers="keys", tablefmt="latex_raw")
            latex_tables[name] = t_latex
                
        return delta_dict, latex_tables
            
        
        
    
### ARCHIVE ###
def SimpleRecorder(prob, recorder = None, name='cases.sql'):
    if not recorder:
        recorder = om.SqliteRecorder(name, record_viewer_data=False)
        
    prob.add_recorder(recorder)
    prob.recording_options['record_desvars'] = True
    prob.recording_options['record_responses'] = True
    prob.recording_options['record_objectives'] = True
    prob.recording_options['record_constraints'] = True
    prob.recording_options['record_inputs'] = True
    
    prob.recording_options["record_rel_error"] = True
    prob.recording_options["record_residuals"] = True
    
    prob.recording_options['includes'] = ["*"]
    
    return prob

def OptiRecorder(prob, name='cases.sql'):
    recorder = om.SqliteRecorder(name, record_viewer_data=False)
    prob.add_recorder(recorder)
    prob.recording_options['record_desvars'] = True
    prob.recording_options['record_responses'] = True
    prob.recording_options['record_objectives'] = True
    prob.recording_options['record_constraints'] = True
    prob.recording_options['record_inputs'] = True
    
    prob.recording_options["record_rel_error"] = True
    prob.recording_options["record_residuals"] = True
    
    prob.recording_options['includes'] = ["*"]
    
    driver = prob.driver
    driver.add_recorder(recorder)
    driver.recording_options['includes'] = ['*']
    driver.recording_options['record_objectives'] = True
    driver.recording_options['record_constraints'] = True
    driver.recording_options['record_desvars'] = True
    driver.recording_options['record_inputs'] = False
    driver.recording_options['record_outputs'] = False
    driver.recording_options['record_residuals'] = False
    
    return prob