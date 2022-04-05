# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:47:29 2022

@author: renkert2
"""

import openmdao.api as om

class Recorder:
    def __init__(self, recorder = None, name='cases.sql'):
        if not recorder:
            recorder = om.SqliteRecorder(name, record_viewer_data=False)
        self.recorder = recorder
        
    def add_to_prob(self, prob):
        prob.add_recorder(self.recorder)
        prob.recording_options['record_desvars'] = True
        prob.recording_options['record_responses'] = True
        prob.recording_options['record_objectives'] = True
        prob.recording_options['record_constraints'] = True
        prob.recording_options['record_inputs'] = True
        
        prob.recording_options["record_rel_error"] = True
        prob.recording_options["record_residuals"] = True
        
        prob.recording_options['includes'] = ["*"]
        
        return prob
    
    def add_to_driver(self, driver):
        driver.add_recorder(self.recorder)
        driver.recording_options['includes'] = ['*']
        driver.recording_options['record_objectives'] = True
        driver.recording_options['record_constraints'] = True
        driver.recording_options['record_desvars'] = True
        driver.recording_options['record_inputs'] = False
        driver.recording_options['record_outputs'] = False
        driver.recording_options['record_residuals'] = False
        
        return driver

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