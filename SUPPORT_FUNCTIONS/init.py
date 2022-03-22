# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:07:49 2022

@author: renkert2
"""

import warnings
import os
import sys
import openmdao.api as om

def init(filepath):
    res_path = os.getenv('ARG_RESEARCH')
    home_path = os.path.join(res_path, 'DymosPlanarQuadrotor')
    if home_path not in sys.path:
        sys.path.append(home_path)
    
def init_output(filepath, suppress_warnings=True):
    os.chdir(os.path.dirname(filepath))
    if not os.path.isdir("Output"):
        os.mkdir("Output")
    os.chdir("Output")
    
    if suppress_warnings:
        warnings.filterwarnings('ignore', category=om.UnitsWarning)