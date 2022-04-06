# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:15:40 2022

@author: renkert2
"""

def scalarize(val):
    if hasattr(val, "__len__"): # Check if array valued
        if len(val) == 1:
            val = val[0] # Get first element in list
        else:
            raise Exception("Scalar values required for upper and lower bounds")
    return val

def iterize(val):
    if hasattr(val, "__iter__"):
        return val
    else:
        return (val,)