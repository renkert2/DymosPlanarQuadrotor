# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 16:07:54 2021

@author: renkert2
"""

import openmdao.api as om
import PlanarBody.PlanarBodyModels as bm
import PlanarPT.PlanarPTModels as pt 
import dymos as dm
import DynamicModel as DM
import os
import Param as P

# CONSTANTS
g = 9.80665

class PlanarSystemParams(P.ParamSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Add Params from Power Train
        pt_params = pt.PlanarPTParams()
        self.update(pt_params)
        
                
        # Temporarily make Propeller params Independent:
        for p in self:
            if p.parent == "Propeller":
                p.dep = False
        
        # Manually Define parameters required for Body Model
        self.add(P.Param(name='rho', val=0.1, desc='Frame Density', strID="rho__Frame", parent="Frame"))
        self.add(P.Param(name='r', val=1, desc='Arm Length', strID="r__Frame", parent = "Frame"))
        
        self.add(P.Param(name='Mass', desc='Frame Mass', strID="Mass__Frame", parent="Frame"))
        self["Mass__Frame"].setDependency(om.ExecComp("Mass=2*r*rho"), {"r":self["r__Frame"], "rho":self["rho__Frame"]})
        self["Mass__Frame"].dep=True
                
        self.add(P.Param("Mass", desc="System Mass", strID="Mass__System", parent="System"))
        c = om.AddSubtractComp(output_name="Mass", input_names=("m_f", "m_pt"))
        self["Mass__System"].setDependency(c, {"m_f":self["Mass__Frame"], "m_pt":self["Mass__PlanarPowerTrain"]})
        self["Mass__System"].dep=True
        
        self.add(P.Param("I", desc="Inertia of Frame about Planar Quadrotor COM", strID="I__Frame", parent="Frame"))
        self["I__Frame"].setDependency(om.ExecComp("I=(1/12)*m*(2*r)**2"), {"m":self["Mass__Frame"], "r":self["r__Frame"]})
        self["I__Frame"].dep=True
        
        # TODO: Add inertia of battery 
        self.add(P.Param("I", desc="Inertia of PowerTrain about Planar Quadrotor COM", strID="I__PlanarPowerTrain", parent="PlanarPowerTrain"))
        self["I__PlanarPowerTrain"].setDependency(om.ExecComp("I=2*(m_prop + m_motor)*r**2"), {"m_prop":self["Mass__Propeller"], "m_motor":self["Mass__Motor"], "r":self["r__Frame"]})
        self["I__PlanarPowerTrain"].dep=True
        
        self.add(P.Param("I", desc="Total Inertia about Planar Quadrotor COM", strID="I__System", parent="System"))
        c = om.AddSubtractComp(output_name="I", input_names=("I_f", "I_pt"))
        self["I__System"].setDependency(c, {"I_f":self["I__Frame"], "I_pt":self["I__PlanarPowerTrain"]})
        self["I__System"].dep=True
        
        self.add(P.Param("HoverThrust", desc="Thrust Requried for Hover", strID="HoverThrust__System", parent="System"))
        self["HoverThrust"].setDependency(om.ExecComp(f"HoverThrust = {g}*m"), {"m":self["Mass__System"]})
        self["HoverThrust"].dep=True
        
class PlanarSystemDynamicModel(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        
    def setup(self):
        nn = self.options["num_nodes"]
        
        self.add_subsystem(name="PT", subsys=pt.PlanarPTModelDAE(num_nodes=nn))
        self.add_subsystem(name="BM", subsys=bm.PlanarBodyODE(num_nodes=nn))
        
        self.connect("PT.y1", "BM.u_1")
        self.connect("PT.y3", "BM.u_2")
        
class PlanarSystemDynamicTraj(DM.DynamicTrajectory):
    def __init__(self, phases, **kwargs):
        super().__init__(phases, linked_vars=['*'], phase_names="phase", **kwargs)
    
    def init_vars(self):
        super().init_vars(openmdao_path = "PT", rename_vars=False, parameter_names = ['theta'], 
                var_opts = {
                    "theta":{'opt':False,'static_target':True}
                    })
        
        self = bm.ModifyTraj(self, openmdao_path="BM")
        
class PlanarSystemDynamicPhase(DM.DynamicPhase):
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
                        output_names = ["y"],
                        var_opts = {"d":{"val":0}})
        ## Add Body Model Information
        # The PlanarQuadrotorODE Module has a method which takes an existing phase
        # and manually adds its states and controls to it.  
        self = bm.ModifyPhase(self, openmdao_path="BM", declare_controls=False)
        
        
class PlanarSystemStaticModel(om.Group):
    def initialize(self):
        self.options.declare("IncludeBody", types=bool, default=False)
        self.options.declare("SolveMode", types=str, default="Forward")
        # SolveMode can be "Forward" to calculate thrust as a function of input, or "Backward" to calculate input as a function of thrust
    
class PlanarSystemModel(P.ParamSystem):
    def __init__(self, traj, **kwargs):
        ps = PlanarSystemParams()
        pg = P.ParamGroup(param_set = ps)
        
        super().__init__(pg, **kwargs)
        
        self._traj = traj
    
    def setup(self):
        # TODO: Add the Static Model Subsystem
        self.add_subsystem("static", pt.PlanarPTModelStatic())
        self.set_input_defaults("static.u1", val=1.0)
        
        # TODO: Add Thrust Ratio
        # tr_comp = bm.PlanarQuadrotorThrustRatio()
        # self.add_subsystem("thrust_ratio", tr_comp)
        
        # Connect output of StaticModel to Thrust Ratio
        #self.connect("static.PT.y1", "thrust_ratio.TMax")
        
        # Add the Dynamic Model Subsystem
        self.add_subsystem("traj", self._traj)
        
        # Run the superclass setup
        super().setup()
    

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
            p.run_model()
        
            # Visualize:
            om.n2(p)
            om.view_connections(p)
            
            # Checks:
            p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
            p.check_partials(compact_print=True, show_only_incorrect=True)
            p.cleanup()
    
    ## Dynamic Model
    print("Checking PlanarSystemDynamicModel")
    
    if not os.path.isdir('./PlanarSystemDynamicModel/'):
        os.mkdir('./PlanarSystemDynamicModel/')
    os.chdir('./PlanarSystemDynamicModel/')
    p = om.Problem(model=PlanarSystemDynamicModel(num_nodes = 10))
    checkProblem(p)
    
    os.chdir('..')
    
    
    ## System Model, Requires Trajectory and Phase
    print("Checking PlanarSystemModel")
        
    if not os.path.isdir('./PlanarSystemModel/'):
        os.mkdir('./PlanarSystemModel/')
    os.chdir('./PlanarSystemModel/')
    
    nn = 20
    tx = dm.GaussLobatto(num_segments=nn)
    phase = PlanarSystemDynamicPhase(transcription=tx)
    phase.init_vars()
    
    traj = PlanarSystemDynamicTraj(phase)
    traj.init_vars()
    
    sys = PlanarSystemModel(traj)
    
    p = om.Problem(model=sys)
    checkProblem(p)

    os.chdir('..')
