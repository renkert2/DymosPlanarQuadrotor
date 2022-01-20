# -*- coding: utf-8 -*-

import os
import DynamicModel as dm
import StaticModel as sm

class PlanarPTModel(dm.DynamicModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPowerTrainModel"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["h", "f", "g"]
        self.options["StaticVars"] = ["theta"]

class PlanarPTStaticModel(sm.StaticModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPowerTrainModel_Simple"
        mdl_path = os.path.dirname(__file__)
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        self.options["Functions"] = ["h", "f", "g"]
    
#%%        
if __name__ == "__main__":
    # Run N2 and Model Checks
    import openmdao.api as om
    import os
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
        
            # Visualize:
            om.n2(p)
            om.view_connections(p)
            
            # Checks:
            p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
            p.check_partials(compact_print=True)
    
    ## Dynamic Model
    print("Checking PlanarPTModel")
    p = om.Problem(model=PlanarPTModel(num_nodes = 10))
    try:
        os.mkdir('./PlanarPTModel/')
    except:
        pass
    os.chdir('./PlanarPTModel/')
    checkProblem(p)
    
    ## Static Model
    print("Checking PlanarPTStaticModel")
    p = om.Problem(model=PlanarPTStaticModel())
    try:
        os.mkdir('./PlanarPTStaticModel/')
    except:
        pass
    os.chdir('./PlanarPTStaticModel/')
    checkProblem(p)