# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 16:07:54 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import PlanarBody.PlanarQuadrotorODE as bm
import PlanarPT.PlanarPTModels as pt 
import PlanarPT.Surrogates.Surrogates as surrogates
import dymos as dm
import DynamicModel as dmm
import os


class PlanarSystemDynamicModel(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('ModelType', types=str, default="DAE")
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        if self.options["ModelType"] == "DAE":
            ptmodel = pt.PlanarPTModelDAE
        elif self.options["ModelType"] == "ODE":
            ptmodel = pt.PlanarPTModelODE
        else:
            raise Exception("Invalid ModelType option")
        
        self.add_subsystem(name="PT", subsys=ptmodel(num_nodes=nn))
        self.add_subsystem(name="BM", subsys=bm.PlanarQuadrotorODE(num_nodes=nn))
        
        self.connect("PT.y1", "BM.u_1")
        self.connect("PT.y3", "BM.u_2")
        
class PlanarSystemStaticModel(om.Group):
    def initialize(self):
        self.options.declare("IncludeBody", types=bool, default=False)
        self.options.declare("SolveMode", types=str, default="Forward")
        # SolveMode can be "Forward" to calculate thrust as a function of input, or "Backward" to calculate input as a function of thrust
        
    def setup(self):
        if self.options["SolveMode"] == "Forward":
            ptmodel = pt.PlanarPTModelDAE_Simple
            self.add_subsystem(name="PT", subsys=ptmodel())
        else:
            # TODO: Reverse Evaluate the PT Model
            pass
            
        if self.options["IncludeBody"]:
            if self.options["SolveMode"] == "Forward":
                 # Calculate Acceleration given Thrust
                 self.add_subsystem(name="BM", subsys=bm.PlanarQuadrotorVertAccel())
                 self.connect("PT.y1", "BM.u")
            if self.options["SolveMode"] == "Backward":
                 # Calculate Thrust given Acceleration
                 self.add_subsystem(name="BM", subsys=bm.PlanarQuadrotorHover())
                 self.connect("BM.u_hover","PT.y1")
        
class PlanarSystemDynamicPhase(dmm.DynamicPhase):
    def __init__(self, **kwargs):
        # Instantiate a Phase and add it to the Trajectory.
        # Here the transcription is necessary but not particularly relevant.
        super().__init__(ode_class=PlanarSystemDynamicModel, **kwargs)
    
        ## Add PowerTrain Information.  In the PlanarSystemDynamicModel, the PlanarPowerTrainModel dynamic model 
        # is added as a subsystem named PT.  When we specify the open_mdao path as PT, init_vars will find the 
        # relevant metadata and use it to add the states, controls, etc to the phase.  The phase variables name will
        # prepend the variable name with the path.  For example, the "x1" state for model.PT.Z would be 
        # referred to as state "PT_Z_x1"
    
    def init_vars(self):
        super().init_vars(openmdao_path="PT", 
                        state_names=["x"],
                        control_names = ["u","d"],
                        parameter_names = ["theta"],
                        #output_names = ["y", "a"],
                        output_names = ["y"],
                        var_opts = {"d":{"val":0}})
        ## Add Body Model Information
        # The PlanarQuadrotorODE Module has a method which takes an existing phase
        # and manually adds its states and controls to it.  
        self = bm.ModifyPhase(self, openmdao_path="BM", declare_controls=False)
    
class PlanarSystemModel(om.Group):
    def __init__(self, dynamic_trajectory, meta, *args, **kwargs):
        self.Traj = dynamic_trajectory
        self.Metadata = meta # Dictionary Metadata from DynamicPhase
        super().__init__(*args, **kwargs)
        
    def initialize(self):
        self.options.declare("IncludeStaticModel", types=bool, default=True)
        self.options.declare("IncludeSurrogates", types=list, default=[])
    
    def setup(self):    
        if "Battery" in self.options["IncludeSurrogates"]:
            bs = surrogates.BatterySurrogate()
            self.add_subsystem('surr_batt', bs)
            
        if "Motor" in self.options["IncludeSurrogates"]:
            ms = surrogates.MotorSurrogate()
            self.add_subsystem('surr_motor', ms)
            
        # Include PlanarQuadrotorSizingComponent
        body_size = bm.PlanarQuadrotorSizeComp()
        self.add_subsystem('size_comp', body_size)
            
        # Add Mass 
        # TODO: Replace with add/subtract comp at some point
        mass_list = ["Mass__Frame", "Mass__Battery", "Mass__Motor", "Mass__Motor", "Mass__Propeller",  "Mass__Propeller"]
        mass_comp = om.AddSubtractComp(output_name="Mass__PlanarQuadrotor", input_names=mass_list)
        self.add_subsystem("mass", mass_comp)
        
        # Add Static Model as Subsystem
        static_model = PlanarSystemStaticModel(IncludeBody=False, SolveMode="Forward")
        self.add_subsystem('static', static_model)
        self.set_input_defaults("static.PT.u1", val=1.0)
        
        # Add Thrust Ratio
        tr_comp = om.ExecComp("TR = TMax / Mass")
        self.add_subsystem("thrust_ratio", tr_comp)

        # Add Trajectory as Subsystem
        self.add_subsystem('traj', self.Traj)
        
        # Add solvers here as necessary
        
        #def configure(self):
        # Configure allows us to issue connections to subsystems when you need information e.g. path names
        # that have been set during the setup of those subsystems.  configure() runs after setup(), 
        # so we can use list_inputs and list_outputs to make more informed connection/promotion choicse
        # See: https://openmdao.org/newdocs/versions/latest/theory_manual/setup_stack.html
        
        # - apparently this doesn't work???  self.list_inputs() returns empty.  
        
        ### Promotions ###
        # Promote PT Parameters to the Dymos trajectory values
        meta = self.Metadata["PT"]
        param_elems = meta["Variable"]["theta"]["Variables"]
        for elem in param_elems:
            desc = elem["Description"]
            theta = elem["Variable"]
            
            to_prom = f'traj.phase0.parameters:PT_{theta}'
            # Dynamic Model
            # Unfortunately, I haven't figured out how to re-promote phase parameters back up to their original name.  
            # For now, we'll have to promote/connect things to the names that Dymos enforces.
            #self.promotes('traj', inputs=[(f'phase0.parameters:PT_{theta}', desc)])
            
            # Static Model
            # Promote the parameters as their Dymos name
            self.promotes('static', inputs=[(f"PT.{theta}", to_prom)])
            #self.promotes('static', inputs=[(f"PT.{theta}", desc)])
            
            # Promote parameters in Mass component
            if desc in mass_list:
                self.promotes('mass', any=[(desc, to_prom)])
            
            # Promote parameters from surrogate models
            if "Battery" in self.options["IncludeSurrogates"]:
                if desc in ["N_s__Battery", "Q__Battery", "R_s__Battery", "Mass__Battery"]:
                    self.promotes("surr_batt", any=[(desc, to_prom)])
            if "Motor" in self.options["IncludeSurrogates"]:
                if desc in ["kV__Motor", "Rm__Motor", "Mass__Motor", "D__Motor", "J__Motor"]:
                    self.promotes("surr_motor", any=[(desc, to_prom)])
                    
            # Promote parameters from sizing component
            if desc in ["Mass__Motor", "Mass__Propeller"]:
                self.promotes("size_comp", inputs=[(desc, to_prom)])
        
        # Promote BM Parameters
        self.connect("size_comp.Mass__Frame", "mass.Mass__Frame")
        self.connect("size_comp.I", "traj.phase0.parameters:BM_I")
        self.promotes("size_comp", inputs=[("r", "traj.phase0.parameters:BM_r")])
        self.connect("mass.Mass__PlanarQuadrotor", "traj.phase0.parameters:BM_m")
        self.connect("mass.Mass__PlanarQuadrotor", "thrust_ratio.Mass")
        
        ### Connections ###
        # Connect output of StaticModel to Thrust Ratio
        self.connect("static.PT.y1", "thrust_ratio.TMax")
        pass

if __name__ == "__main__":
    # Run N2 and Model Checks
    import openmdao.api as om
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    os.chdir(os.path.dirname(__file__))
    try:
        os.mkdir('./ModelChecks/')
    except:
        pass
    os.chdir('./ModelChecks/')
    
    def checkProblem(p):
            p.setup()
            #p.final_setup()
        
            # Visualize:
            om.n2(p)
            om.view_connections(p)
            
            # Checks:
            #p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
            #p.check_partials(compact_print=True)
    
    ## Dynamic Model
    # print("Checking PlanarSystemDynamicModel")
    
    # if not os.path.isdir('./PlanarSystemDynamicModel_DAE/'):
    #     os.mkdir('./PlanarSystemDynamicModel_DAE/')
    # os.chdir('./PlanarSystemDynamicModel_DAE/')
    # p = om.Problem(model=PlanarSystemDynamicModel(num_nodes = 10, ModelType="DAE"))
    # checkProblem(p)
    
    # os.chdir('..')
    
    # if not os.path.isdir('./PlanarSystemDynamicModel_ODE/'):
    #     os.mkdir('./PlanarSystemDynamicModel_ODE/')
    # os.chdir('./PlanarSystemDynamicModel_ODE/')
    # p = om.Problem(model=PlanarSystemDynamicModel(num_nodes = 10, ModelType="ODE"))
    # checkProblem(p)
    
    # os.chdir('..')
    
    # if not os.path.isdir('./PlanarSystemStaticModel_Forward/'):
    #     os.mkdir('./PlanarSystemStaticModel_Forward/')
    # os.chdir('./PlanarSystemStaticModel_Forward/')
    # p = om.Problem(model=PlanarSystemStaticModel(IncludeBody=True, SolveMode="Forward"))
    # checkProblem(p)
    
    # os.chdir('..')
    
    ## System Model, Requires Trajectory and Phase
    nn = 20
    tx = dm.GaussLobatto(num_segments=nn)
    phase = PlanarSystemDynamicPhase(transcription=tx)
    phase.init_vars()
    meta = phase.Metadata
    traj = dm.Trajectory()
    traj.add_phase('phase0', phase)
    
    
    if not os.path.isdir('./PlanarSystemModel_Surrogates/'):
        os.mkdir('./PlanarSystemModel_Surrogates/')
    os.chdir('./PlanarSystemModel_Surrogates/')
    p = om.Problem(model=PlanarSystemModel(traj, meta, IncludeSurrogates=["Battery", "Motor"], IncludeStaticModel=True))
    checkProblem(p)
    
    os.chdir('..')
    
    if not os.path.isdir('./PlanarSystemModel_NoSurrogates/'):
        os.mkdir('./PlanarSystemModel_NoSurrogates/')
    os.chdir('./PlanarSystemModel_NoSurrogates/')
    p = om.Problem(model=PlanarSystemModel(traj, meta, IncludeSurrogates=[], IncludeStaticModel=True))
    checkProblem(p)

