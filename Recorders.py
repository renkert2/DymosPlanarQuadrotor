# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:47:29 2022

@author: renkert2
"""

import openmdao.api as om

def SimpleRecorder(prob):
    recorder = om.SqliteRecorder('cases.sql', record_viewer_data=False)
    prob.add_recorder(recorder)
    prob.recording_options['record_desvars'] = True
    prob.recording_options['record_responses'] = True
    prob.recording_options['record_objectives'] = True
    prob.recording_options['record_constraints'] = True
    prob.recording_options['record_inputs'] = True
    prob.recording_options['includes'] = ["*"]
    
    return prob