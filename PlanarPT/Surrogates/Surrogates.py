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

class MotorSurrogate(om.ExplicitComponent):
    def setup(self):
        self.add_input(name='kV__Motor', shape=(1,), val=965, desc='Motor speed constant')
        self.add_input(name='Rm__Motor', shape=(1,), val=0.102, desc='Motor phase resistance')

        self.add_output(name='Mass__Motor', shape=(1,), desc='Motor mass')
        self.add_output(name='D__Motor', shape=(1,), desc='Motor diameter')
        self.add_output(name="J__Motor", shape=(1,), desc='Motor inertia')

        #self.declare_partials(of='*', wrt='*', method='fd') # Would eventually want to include analytical derivatives
        self.declare_partials(of='*', wrt='*', method='exact')

    
    def compute(self, inputs, outputs):
        kV = inputs["kV__Motor"]
        Rm = inputs["Rm__Motor"]
        
        # Variables
        [x,y] = [kV,Rm]

        ## Model 1 - Mass
        # Fit Coefficients
        [a,b,c,d,e,f,g]=[73.3029,0.0225,0.0000,1.1549,2.9988,0.0999,0.0074]
        M = (a/(x+f))**(d) + (b/(y+g))**(e) + c
        
        ## Model 2 - D
        # Fit Coefficients
        [a,b,c,d,e,f,g]=[121.8487,0.0012,0.0165,2.0226,1.2217,371.9432,0.0001]
        D = (a/(x+f))**(d) + (b/(y+g))**(e) + c
        
        outputs["Mass__Motor"] = M
        outputs["D__Motor"] = D
        outputs["J__Motor"] = (M/2)*(D/2)**2;

    def compute_partials(self, inputs, partials):
        x = inputs["kV__Motor"]
        y = inputs["Rm__Motor"]

        # Model 1 - Mass
        [a,b,c,d,e,f,g]=[73.3029,0.0225,0.0000,1.1549,2.9988,0.0999,0.0074]
        partials["Mass__Motor", "kV__Motor"] = -((a*d*(a/(f + x))**(-1 + d))/(f + x)**2)
        partials["Mass__Motor", "Rm__Motor"] = -((b*e*(b/(g + y))**(-1 + e))/(g + y)**2)

        # Model 2 - D
        [a,b,c,d,e,f,g]=[121.8487,0.0012,0.0165,2.0226,1.2217,371.9432,0.0001]
        partials["D__Motor", "kV__Motor"] = -((a*d*(a/(f + x))**(-1 + d))/(f + x)**2)
        partials["D__Motor", "Rm__Motor"] = -((b*e*(b/(g + y))**(-1 + e))/(g + y)**2)