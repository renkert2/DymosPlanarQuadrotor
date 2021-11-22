# -*- coding: utf-8 -*-

import DymosModel as dmm

class PlanarPTModel(dmm.DymosModel):
    def initialize(self):
        super().initialize()
        
        mdl = "PlanarPowerTrainModel"
        mdl_path = 'C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor/PlanarPT' # Point Model to folder containing the Model folder.  This is required for !openmdao check functions
        self.options["Model"] = mdl
        self.options["Path"] = mdl_path
        