# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 16:28:42 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om

class PowertrainODE(om.ExplicitComponent):

    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options['num_nodes']
        
        ### DYNAMIC STATES ###
        # =============================================================================
        #             State Variable               Description           
        #     ______________    _________________________________
        # 
        #          "x1"         "Battery \ Battery SOC"          
        #          "x2"         "Motor \ Inductance (i_q)"       
        #          "x3"         "MotorProp_1 \ Inertia (omega_m)"
        #          "x4"         "Motor \ Inductance (i_q)"       
        #          "x5"         "MotorProp_2 \ Inertia (omega_m)"
        #          "x6"         "Motor \ Inductance (i_q)"       
        #          "x7"         "MotorProp_3 \ Inertia (omega_m)"
        #          "x8"         "Motor \ Inductance (i_q)"       
        #          "x9"         "MotorProp_4 \ Inertia (omega_m)"
        # =============================================================================
        units = [""]
        for i in range(9):
            self.add_input(name=('x'+str(i)), shape=(nn,))
        
        ### INPUTS ###
        # =============================================================================
        #             Input Variable        Description     
        #     ______________    ____________________
        # 
        #          "u1"         "PMSMInverter_1 \ d"
        #          "u2"         "PMSMInverter_2 \ d"
        #          "u3"         "PMSMInverter_3 \ d"
        #          "u4"         "PMSMInverter_4 \ d"
        # =============================================================================

        ### DISTURBANCES ###
        #None#
        
        ### PARAMETERS ###
        # D__Propeller
        # J__Motor
        # J__Propeller
        # N_p__Battery
        # N_s__Battery
        # Q__Battery
        # R_1__PMSMInverter 
        # R_s__Battery
        # Rm__Motor
        # V_OCV_nom__Battery - Will eventually be made a function of q
        # kV__Motor
        # k_P__Propeller
        # k_P_mod__Propeller
        
        
    def compute(self, inputs, outputs):
        # =============================================================================
        # "-(5*(6**(1/2)*u1*x2 + 6**(1/2)*u2*x4 + 6**(1/2)*u3*x6 + 6**(1/2)*u4*x8))/(36*N_p__Battery*Q__Battery)"
        # "-(2305843009213693952*(30000*2**(1/2)*3**(1/2)*N_p__Battery*x3 + 3000*N_p__Battery*R_1__PMSMInverter*kV__Motor*x2*np.pi + 2000*N_p__Battery*Rm__Motor*kV__Motor*x2*np.pi + 9*N_p__Battery*kV__Motor*u1**2*x2*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1**2*x2*np.pi + 9*N_p__Battery*kV__Motor*u1*u2*x4*np.pi + 9*N_p__Battery*kV__Motor*u1*u3*x6*np.pi + 9*N_p__Battery*kV__Motor*u1*u4*x8*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1*u2*x4*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1*u3*x6*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1*u4*x8*np.pi - 1000*6**(1/2)*N_p__Battery*N_s__Battery*V_OCV_nom__Battery*kV__Motor*u1*np.pi))/(539567264156004375*N_p__Battery*kV__Motor*np.pi)"
        # "(1041767500852505625*2**(1/2)*3**(1/2)*x2 - 1059929209176064*D__Propeller**5*kV__Motor*k_P__Propeller*k_P_mod__Propeller*x3**2)/(69451166723500375*kV__Motor*np.pi*(J__Motor + J__Propeller))"
        # "-(2305843009213693952*(30000*2**(1/2)*3**(1/2)*N_p__Battery*x5 + 3000*N_p__Battery*R_1__PMSMInverter*kV__Motor*x4*np.pi + 2000*N_p__Battery*Rm__Motor*kV__Motor*x4*np.pi + 9*N_p__Battery*kV__Motor*u2**2*x4*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u2**2*x4*np.pi + 9*N_p__Battery*kV__Motor*u1*u2*x2*np.pi + 9*N_p__Battery*kV__Motor*u2*u3*x6*np.pi + 9*N_p__Battery*kV__Motor*u2*u4*x8*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1*u2*x2*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u2*u3*x6*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u2*u4*x8*np.pi - 1000*6**(1/2)*N_p__Battery*N_s__Battery*V_OCV_nom__Battery*kV__Motor*u2*np.pi))/(539567264156004375*N_p__Battery*kV__Motor*np.pi)"
        # "(1041767500852505625*2**(1/2)*3**(1/2)*x4 - 1059929209176064*D__Propeller**5*kV__Motor*k_P__Propeller*k_P_mod__Propeller*x5**2)/(69451166723500375*kV__Motor*np.pi*(J__Motor + J__Propeller))"
        # "-(2305843009213693952*(30000*2**(1/2)*3**(1/2)*N_p__Battery*x7 + 3000*N_p__Battery*R_1__PMSMInverter*kV__Motor*x6*np.pi + 2000*N_p__Battery*Rm__Motor*kV__Motor*x6*np.pi + 9*N_p__Battery*kV__Motor*u3**2*x6*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u3**2*x6*np.pi + 9*N_p__Battery*kV__Motor*u1*u3*x2*np.pi + 9*N_p__Battery*kV__Motor*u2*u3*x4*np.pi + 9*N_p__Battery*kV__Motor*u3*u4*x8*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1*u3*x2*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u2*u3*x4*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u3*u4*x8*np.pi - 1000*6**(1/2)*N_p__Battery*N_s__Battery*V_OCV_nom__Battery*kV__Motor*u3*np.pi))/(539567264156004375*N_p__Battery*kV__Motor*np.pi)"
        # "(1041767500852505625*2**(1/2)*3**(1/2)*x6 - 1059929209176064*D__Propeller**5*kV__Motor*k_P__Propeller*k_P_mod__Propeller*x7**2)/(69451166723500375*kV__Motor*np.pi*(J__Motor + J__Propeller))"
        # "-(2305843009213693952*(30000*2**(1/2)*3**(1/2)*N_p__Battery*x9 + 3000*N_p__Battery*R_1__PMSMInverter*kV__Motor*x8*np.pi + 2000*N_p__Battery*Rm__Motor*kV__Motor*x8*np.pi + 9*N_p__Battery*kV__Motor*u4**2*x8*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u4**2*x8*np.pi + 9*N_p__Battery*kV__Motor*u1*u4*x2*np.pi + 9*N_p__Battery*kV__Motor*u2*u4*x4*np.pi + 9*N_p__Battery*kV__Motor*u3*u4*x6*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u1*u4*x2*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u2*u4*x4*np.pi + 3000*N_s__Battery*R_s__Battery*kV__Motor*u3*u4*x6*np.pi - 1000*6**(1/2)*N_p__Battery*N_s__Battery*V_OCV_nom__Battery*kV__Motor*u4*np.pi))/(539567264156004375*N_p__Battery*kV__Motor*np.pi)"
        # "(1041767500852505625*2**(1/2)*3**(1/2)*x8 - 1059929209176064*D__Propeller**5*kV__Motor*k_P__Propeller*k_P_mod__Propeller*x9**2)/(69451166723500375*kV__Motor*np.pi*(J__Motor + J__Propeller))"           
        # =============================================================================
        
    
    def compute_partials(self, inputs, partials):
        