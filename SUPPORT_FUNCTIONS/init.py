# -*- coding: utf-8 -*-
"""
Created on Fri Jan 28 17:07:49 2022

@author: renkert2
"""

import warnings
import os
import sys
import openmdao.api as om

HOME_PATH =  os.path.join(os.getenv('ARG_RESEARCH'), 'DymosPlanarQuadrotor')
if HOME_PATH not in sys.path:
    sys.path.append(HOME_PATH)

INPUT_OPT_PATH = os.path.join(HOME_PATH, "STUDIES", "InputOptimization", "Output")
if INPUT_OPT_PATH not in sys.path:
    sys.path.append(INPUT_OPT_PATH)

def init_output(filepath, dirname="Output", suppress_warnings=True):
    os.chdir(os.path.dirname(filepath))
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    os.chdir(dirname)
    
    if suppress_warnings:
        warnings.filterwarnings('ignore', category=om.UnitsWarning)