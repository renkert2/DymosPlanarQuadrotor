# -*- coding: utf-8 -*-

import os
import DynamicModel as dm
import StaticModel as sm
        

class PlanarPTModelDAE(dm.DynamicModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPTModelDAE"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["h", "f", "g"]
        self.options["StaticVars"] = ["theta"]

class PlanarPTModelODE(dm.DynamicModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPTModelODE"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["f", "g"]
        self.options["StaticVars"] = ["theta"]

class PlanarPTModelDAE_Simple(sm.StaticModel):
    # TODO: Add a version of this that calculates u_ss as a function of thrust

    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPTModelDAE_Simple"
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
    
    model_types = [PlanarPTModelDAE, PlanarPTModelODE, PlanarPTModelDAE_Simple]
    
    for mtype in model_types:
        checkModelClass(mtype)
    