# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 11:58:59 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om

class BatterySurrogate(om.ExplicitComponent):
    def setup(self):
        self.add_input(name='N_s__Battery', shape=(1,), val=4, desc='Battery Series Cells')
        self.add_input(name='Q__Battery', shape=(1,), val=4000, desc='Battery Capacity')

        self.add_output(name='R_s__Battery', shape=(1,), desc='Battery series resistance')
        self.add_output(name='Mass__Battery', shape=(1,), desc='Battery mass')

        #self.declare_partials(of='*', wrt='*', method='fd') # Would eventually want to include analytical derivatives
        self.declare_partials(of='*', wrt='*', method='exact')

    
    def compute(self, inputs, outputs):
        N_s = inputs["N_s__Battery"]
        Q = inputs["Q__Battery"]
        
        # Variables
        [x,y] = [N_s,Q]

        ## Model 1 - R_s
        # Fit Coefficients
        [a,b,c,d,k]=[7.6718,-106.5089,-8.1192,0.5972,8.1217]
        outputs["R_s__Battery"] = a/(y+b)+c*x**(d/y) +k
        
        ## Model 2 - Mass
        # Fit Coefficients
        [a,b] = [3.1324e-05, 0.019376]
        outputs["Mass__Battery"] = a*x*y+b

    def compute_partials(self, inputs, partials):
        x = inputs["N_s__Battery"]
        y = inputs["Q__Battery"]

        # Model 1 - R_s
        [a,b,c,d,k]=[7.6718,-106.5089,-8.1192,0.5972,8.1217]
        partials["R_s__Battery", "N_s__Battery"] = (c*d*x**(-1 + d/y))/y
        partials["R_s__Battery", "Q__Battery"] = -(a/(b + y)**2) - (c*d*x**(d/y)*np.log(x))/y**2

        # Model 2 - Mass
        [a,b] = [3.1324e-05, 0.019376]
        partials["Mass__Battery", "N_s__Battery"] = a*y
        partials["Mass__Battery", "Q__Battery"] = a*x
