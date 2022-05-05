# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import openmdao.api as om

import SUPPORT_FUNCTIONS.init as init

init.init_output(__file__)

reader = om.CaseReader('search_cases.sql')
print(reader.list_cases())

cases = reader.get_cases("problem")
for case in cases:
    print(case.get_objectives(scaled=False))
    
    
    