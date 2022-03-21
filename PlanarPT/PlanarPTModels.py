# -*- coding: utf-8 -*-

import os
import DynamicModel as dm
import StaticModel as sm
import openmdao.api as om
import Param

class PlanarPTParams(Param.ParamGroup):
    def __init__(self, **kwargs):
        ps = Param.ParamSet()
        f = open(os.path.join(os.path.dirname(__file__), "PlanarPTModelDAE", "ParamMetadata.json"))
        ps.load(f)
        
        # Temporarily make Propeller params Independent:
        for p in ps:
            if p.parent == "Propeller":
                p.dep = False
 
        super().__init__(param_set=ps,**kwargs)

class PlanarPTDynamicTraj(dm.DynamicTrajectory):
    def __init__(self, phases, **kwargs):
        super().__init__(phases, linked_vars=['*'], phase_names="phase", **kwargs)
    
    def init_vars(self):
        super().init_vars(openmdao_path = "", parameter_names = ['theta'], 
                var_opts = {
                    "theta":{'opt':False,'static_target':True}
                    })

class PlanarPTDynamicPhase(dm.DynamicPhase):
    def __init__(self, **kwargs):
        # Instantiate a Phase and add it to the Trajectory.
        # Here the transcription is necessary but not particularly relevant.
        super().__init__(ode_class=PlanarPTModelDAE, **kwargs)
    
    def init_vars(self):
        super().init_vars(state_names=["x"],
                        control_names = ["u","d"],
                        #parameter_names = ["theta"], # We want to declare the parameters in the trajectory
                        #output_names = ["y", "a"],
                        output_names = ["y"],
                        var_opts = {"x":{"fix_initial":True}})

class PlanarPTModelDAE(dm.DynamicModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPTModelDAE"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["h", "f", "g"]
        self.options["StaticVars"] = ["theta"]
    
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
    
    def checkModelClass(model_class):
        class_name = model_class.__name__
        
        if not os.path.isdir(class_name):
            os.mkdir(class_name)
        os.chdir(class_name)
        
        print(f"Checking Model Class: {class_name}")
        
        if issubclass(model_class, dm.DynamicModel):
            mdl_args = {"num_nodes":10}
        else:
            mdl_args = {}
        p = om.Problem(model=model_class(**mdl_args))
        p.setup()
        p.final_setup()
        
        # Visualize:
        om.n2(p)
        om.view_connections(p)
        
        # Checks:
        p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
        p.check_partials(compact_print=True)
        
        os.chdir('..')
    
    #model_types = [PlanarPTModelDAE, PlanarPTModelDAE_Simple]
    model_types = [PlanarPTModelDAE]
    
    for mtype in model_types:
        checkModelClass(mtype)
    