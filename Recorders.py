# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:47:29 2022

@author: renkert2
"""

import openmdao.api as om
import os

class Recorder:
    def __init__(self, recorder = None, sim_recorder=None, name='cases.sql'):
        name, ext = os.path.splitext(name)
        
        if not recorder:
            recorder = om.SqliteRecorder(name+ext, record_viewer_data=False)
        self.recorder = recorder
        
        if not sim_recorder:
            sim_recorder = om.SqliteRecorder(name+"_sim"+ext, record_viewer_data=False)
        self.sim_recorder = sim_recorder
        
        self.prob = None
        
        self.traj = None
        self.sim_prob = None
        
        self.driver = None
        
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
        driver.recording_options['includes'] = ['*']
        driver.recording_options['record_objectives'] = True
        driver.recording_options['record_constraints'] = True
        driver.recording_options['record_desvars'] = True
        driver.recording_options['record_inputs'] = False
        driver.recording_options['record_outputs'] = False
        driver.recording_options['record_residuals'] = False
        
        self.driver = driver
        return driver
    
    def add_traj(self, traj):
        self.traj = traj
        self.sim_prob = traj.simulate()
        self.sim_prob.add_recorder(self.sim_recorder)
        
    def record(self, case="final"):
        if self.prob:
            self.prob.record(case)
        if self.traj:
            self.sim_prob.run_model()
            self.sim_prob.record(case+"_sim")
        
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