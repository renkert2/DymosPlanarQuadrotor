# -*- coding: utf-8 -*-
"""
Created on Mon May 16 14:23:55 2022

@author: renkert2
"""
import numpy as np
import openmdao.api as om

from GraphTools_Phil_V2.OpenMDAO import Param as P


class IndexParamComp(om.ExplicitComponent, P._ParamComp_Super):
    def __init__(self, set_vals=None,**kwargs):
        super().__init__(**kwargs)
        self.set_vals = set_vals # List or set whose index corresponds to the parameter value
    
    def setup(self):
        self.add_discrete_input("i", val=0, desc="Selection index")
        self.add_output(self._param.name, val=np.nan, desc=f"Discrete output for {self._param.strID}")
    
    def compute(self, inputs, outputs):
        if self._param.dep:
            val = self.set_vals[round(inputs["i"])]
        else:
            val = self._param.val
        
        for key in outputs:
            outputs[key] = val
 