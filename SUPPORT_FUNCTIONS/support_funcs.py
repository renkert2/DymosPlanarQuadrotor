# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:15:40 2022

@author: renkert2
"""

def scalarize(val):
    if hasattr(val, "__len__") and len(val) == 1: # Check if array valued
        val = val[0] # Get first element in list
    return val

def iterize(val):
    if (not isinstance(val, str)) and hasattr(val, "__iter__"):
        return val
    else:
        return (val,)
    
def flatten(l, ltypes=(list, tuple)):
    # From: http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)