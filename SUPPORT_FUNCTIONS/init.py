# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:07:49 2022

@author: renkert2
"""

import warnings
import os
import openmdao.api as om

def init_study(filepath, suppress_warnings=True):
    os.chdir(os.path.dirname(filepath))
    if not os.path.isdir("Output"):
        os.mkdir("Output")
    os.chdir("Output")
    
    if suppress_warnings:
        warnings.filterwarnings('ignore', category=om.UnitsWarning)