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
import PlanarPT.SUPPORT.Surrogate as S
import SUPPORT_FUNCTIONS.init as init
import matplotlib.pyplot as plt
import Constraints as C

# CONSTANTS
g = 9.80665

class PlanarSystemSurrogates:
    def __init__(self, params):
        surr_path = os.path.join(init.HOME_PATH, "PlanarPT/PlanarPTModelDAE/SurrogateMetadata.json")
        f = open(surr_path)
        self.surrogates = S.Surrogate.load(f, params)
    
    def __getitem__(self, val):
        return self.surrogates[val]
    
    def items(self):
        return self.surrogates.items()
    
    def setup(self):
        for s in self.surrogates:
            self.surrogates[s].setup()
        
    def plot_boundary_3D(self):
        figs = []
        for i,pair in enumerate(self.surrogates.items()):
            fig = plt.figure(i)
            pair[1].plot_boundary_3D(fig = fig)
            
            figs.append(fig)
        return figs
 
        
class PlanarSystemParams(P.ParamSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Add Params from Power Train
        pt_params = pt.PlanarPTParams()
        self.update(pt_params)

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
        
class PlanarSystemDAE(om.Group):
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
        super().__init__(ode_class=PlanarSystemDAE, **kwargs)
    
        ## Add PowerTrain Information.  In the PlanarSystemDynamicModel, the PlanarPowerTrainModel dynamic model 
        # is added as a subsystem named PT.  When we specify the open_mdao path as PT, init_vars will find the 
        # relevant metadata and use it to add the states, controls, etc to the phase.  The phase variables name will
        # prepend the variable name with the path.  For example, the "x1" state for model.PT.Z would be 
        # referred to as state "PT_Z_x1"
    
    def init_vars(self):
        super().init_vars(openmdao_path="PT", 
                        state_names=["x"],
                        control_names = ["u","d"],
                        output_names = ["y", "a"],
                        var_opts = {"d":{"val":0}})
        ## Add Body Model Information
        # The PlanarQuadrotorODE Module has a method which takes an existing phase
        # and manually adds its states and controls to it.  
        self = bm.ModifyPhase(self, openmdao_path="BM", declare_controls=False)
        
class PlanarSystemModel(P.ParamSystem):
    def __init__(self, traj, cons = None, **kwargs):
        ps = PlanarSystemParams()
        psurr = PlanarSystemSurrogates(params=ps)
        pg = P.ParamGroup(param_set = ps)
        
        super().__init__(pg, **kwargs)
        
        self._traj = traj
        self.surrogates = psurr
        
        if cons==None:
            cons = C.ConstraintSet() # Create an empty constraint set
            cons.add(C.BatteryCurrent())
        elif not isinstance(cons, C.ConstraintSet):
            raise Exception("cons argument must be a constraint set")
            
        self.cons = cons # Problem Constraints
    
    def setup(self):
        # Setup the Surrogates
        self.surrogates.setup()
        
        ### Build the Model ###
        # Attach the surrogate fits
        for (n,s) in self.surrogates.items():
            s.fits.attach_outputs()
        
        self.setup_post() # Defined in Subclasses
        
        ### Constraints ### 
        for c in self.cons:
            if isinstance(c, C.ConstraintParam):
                c.set_bounds(self._param_group)
            if isinstance(c, C.ConstraintComp):
                c.add_to_system(self)
            if isinstance(c, C.TrajConstraint):
                c.add_to_traj(self._traj)
              
        # Add the Dynamic Model Subsystem
        self.add_subsystem("traj", self._traj)
        
        # Run the superclass setup
        super().setup()
    
    def setup_post(self):
        # Reserved for subclasses
        pass
    
class PlanarSystemDesignModel(PlanarSystemModel):
    # Adds additional components, design variables, and constraints requried for 
    # plant optimization in the continuous domain. 
    
    def __init__(self, traj, des_cons = None, **kwargs):
        super().__init__(traj, **kwargs)
        if des_cons == None:
            des_cons = C.ConstraintSet()
            des_cons.add(C.ThrustRatio())
        elif not isinstance(des_cons, C.ConstraintSet):
            raise Exception("cons argument must be a constraint set")
        self.cons.add(des_cons)
    
    def initialize(self):
        super().initialize()
        self.options.declare('opt_comps', types=dict, default={})
    
    def setup_post(self):
        # Attach the boundary constraint components
        for (n,s) in self.surrogates.items():
            s.boundary.attach_args()
            s.boundary.add_to_system(self, name=f"{n}_boundary")

        # Add the Static Model Subsystem
        self.add_subsystem("static", pt.PlanarPTModelStatic())
        self.set_input_defaults("static.u1", val=1.0)
    
        ### Design Variables ###
        opt_comps = self.options["opt_comps"]
        for c in opt_comps:
            s = self.surrogates[c]
            for p in s.fits.inputs:
                if not opt_comps[c]: 
                    p.opt = True
                elif (p.strID in opt_comps[c]) or (p.name in opt_comps[c]): 
                    p.opt = True
                else:
                    p.opt = False


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
            p.final_setup()
            #om.n2(p, outfile="n2_prerun.html")
            p.run_model()
        
            # Visualize:
            om.n2(p)
            #om.view_connections(p)
            
            # Checks:
            #p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
            p.check_partials(compact_print=True, show_only_incorrect=True)
            p.cleanup()
            
            # Print Constraints
            print(p.list_problem_vars())
    
    ## Dynamic Model
    print("Checking PlanarSystemDAE")
    
    if not os.path.isdir('./PlanarSystemDAE/'):
        os.mkdir('./PlanarSystemDAE/')
    os.chdir('./PlanarSystemDAE/')
    p = om.Problem(model=PlanarSystemDAE(num_nodes = 10))
    #checkProblem(p)
    
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
    
    ## System Design Model, Requires Trajectory and Phase
    print("Checking PlanarSystemDesignModel")
        
    if not os.path.isdir('./PlanarSystemDesignModel/'):
        os.mkdir('./PlanarSystemDesignModel/')
    os.chdir('./PlanarSystemDesignModel/')
    
    nn = 20
    tx = dm.GaussLobatto(num_segments=nn)
    phase = PlanarSystemDynamicPhase(transcription=tx)
    phase.init_vars()
    
    traj = PlanarSystemDynamicTraj(phase)
    traj.init_vars()
    
    sys = PlanarSystemDesignModel(traj)
    
    p = om.Problem(model=sys)
    checkProblem(p)
    
    

    os.chdir('..')
