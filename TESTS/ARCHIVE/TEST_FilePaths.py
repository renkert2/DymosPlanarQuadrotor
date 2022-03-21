# -*- coding: utf-8 -*-
"""
Created on Fri Nov 12 10:09:49 2021

@author: renkert2
"""

import os
print(__file__)
print(os.path.join(os.path.dirname(__file__), '..'))
print(os.path.dirname(os.path.realpath(__file__)))
print(os.path.abspath(os.path.dirname(__file__)))