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

# Get Latest Weekly Report Directory
def get_latest_directory(directory=os.getenv("WEEKLY_REPORTS"), method="FolderName", date_format = "MMddyyyy"):
    pass

def init_output(filepath, suppress_warnings=True):
    os.chdir(os.path.dirname(filepath))
    if not os.path.isdir("Output"):
        os.mkdir("Output")
    os.chdir("Output")
    
    if suppress_warnings:
        warnings.filterwarnings('ignore', category=om.UnitsWarning)