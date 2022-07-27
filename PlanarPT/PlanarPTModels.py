# -*- coding: utf-8 -*-

import os
import DynamicModel as dm
import StaticModel as sm
import openmdao.api as om
import Param as P
import PlanarPT.PlanarPT_Controller as pptc

class PlanarPTParams(P.ParamSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        f = open(os.path.join(os.path.dirname(__file__), "PlanarPTModelDAE", "ParamMetadata.json"))
        self = self.load(f)
        pass
        
class PlanarPTDynamicTraj(dm.DynamicTrajectory):
    def __init__(self, phases, **kwargs):
        super().__init__(phases, linked_vars=['*'], phase_names="phase", **kwargs)
    
    def init_vars(self, **kwargs):
        super().init_vars(parameter_names = ['theta'], 
                var_opts = {
                    "theta":{'opt':False,'static_target':True}
                    },
                **kwargs)

class PlanarPTDynamicPhase(dm.DynamicPhase):
    def __init__(self, include_controller=False, **kwargs):
        # Instantiate a Phase and add it to the Trajectory.
        # Here the transcription is necessary but not particularly relevant.
        self.include_controller = include_controller
        super().__init__(ode_class=PlanarPTSystemDAE,  model_kwargs={"include_controller":include_controller}, **kwargs)
    
    def init_vars(self, **kwargs):
        control_names = ["d"]
        if not self.include_controller:
            control_names.append("u")
        
        super().init_vars(state_names=["x"],
                        control_names = control_names,
                        #parameter_names = ["theta"], # We want to declare the parameters in the trajectory
                        #output_names = ["y", "a"],
                        output_names = ["y"],
                        var_opts = {"x":{"fix_initial":True}},
                        **kwargs)

class PlanarPTModelDAE(dm.DynamicModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPTModelDAE"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["h", "f", "g"]
        self.options["StaticVars"] = ["theta"]
        
class PlanarPTSystemDAE(om.Group):
    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('include_controller', types=bool, default=False)
        
    def setup(self):
        nn = self.options["num_nodes"]
        include_controller = self.options["include_controller"]
        
        if include_controller:
            self.add_subsystem(name="CTRL", subsys=pptc.PlanarController(num_nodes=nn))
        self.add_subsystem(name="PT", subsys=PlanarPTModelDAE(num_nodes=nn))

        if include_controller:
            self.connect("CTRL.u_1", "PT.u1")
            self.connect("CTRL.u_2", "PT.u2")        
        
class PlanarPTModelStatic(sm.StaticModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPTModelSimple"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["h", "f", "g"]
    
#%%        
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
    
    model = PlanarPTSystemDAE(include_controller=True, num_nodes=10)

    p = om.Problem(model=model)
    p.setup()
    p.final_setup()
    
    # Visualize:
    om.n2(p)
    om.view_connections(p)
    
    # Checks:
    p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
    p.check_partials(compact_print=True)
    
    os.chdir('..')
    
    
    