# -*- coding: utf-8 -*-
"""
Created on Fri Apr  1 11:32:38 2022

@author: renkert2
"""
import openmdao.api as om
        
class ThrustRatio(om.ExplicitComponent):
    def setup(self):
        self.add_input('HoverThrust__System', val=1, desc='mass')
        self.add_input('TMax', val=1, desc='Maximum thrust')
        
        self.add_output('TR', desc="Thrust Ratio")
    
        self.declare_partials('*', '*', method='exact')
    def compute(self, inputs, outputs):
        ht = inputs['HoverThrust__System']
        TMax = inputs["TMax"]
        outputs["TR"] = TMax / ht
    def compute_partials(self, inputs, partials):
        ht = inputs['HoverThrust__System']
        TMax = inputs["TMax"]
        partials["TR", "HoverThrust__System"] = -TMax/(ht**2)
        partials["TR", "TMax"] = 1/(ht)
        
            # Add Thrust Ratio
        tr_comp = C.ThrustRatio()
        tr_comp.add_to_system(self)
        self.add_subsystem("thrust_ratio", tr_comp, params="HoverThrust__System")
        
                # Connect output of StaticModel to Thrust Ratio
        self.connect("static.y1", "thrust_ratio.TMax")
        
        ### Design Constraints ### 
        self.add_constraint('thrust_ratio.TR', lower=self.options["tr_lower"])