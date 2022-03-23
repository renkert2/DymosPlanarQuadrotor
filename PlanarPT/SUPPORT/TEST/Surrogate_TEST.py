# -*- coding: utf-8 -*-

import os
import sys
home = "C:/Users/renkert2/Documents/ARG_Research/DymosPlanarQuadrotor"
if home not in  sys.path:
    sys.path.append(home)
import PlanarPT.SUPPORT.Surrogate as S
import SUPPORT_FUNCTIONS.init as init
import openmdao.api as om

file_path = os.path.join(init.HOME_PATH, "PlanarPT/PlanarPTModelDAE/SurrogateMetadata.json")
f = open(file_path)
s_dict = S.Surrogate.load(f)

s = s_dict["k_P__Propeller"]
s.setup()

prob = om.Problem()
prob.model.add_subsystem("mm", s.comp)

prob.setup()
prob.final_setup()

prob.set_val('mm.D__Propeller', 0.5)
prob.set_val('mm.P__Propeller', 0.1)

prob.run_model()
print(prob.get_val("mm.k_P__Propeller"))

s.plot()