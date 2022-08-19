# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 18:17:44 2022

@author: renkert2
"""

import os
import sys
import openmdao.api as om
from GraphTools_Phil_V2.OpenMDAO import Param as P

file_dir = os.path.dirname(__file__)
os.chdir(file_dir)

sys_dir = os.path.join(file_dir, "..", "..")
if sys_dir not in sys.path:
    sys.path.append(sys_dir)
import PlanarSystem as ps

psp = ps.PlanarSystemParams()
prob = om.Problem(model=P.ParamGroup(param_set=psp))

prob.setup()
prob.run_model()
om.n2(prob, outfile="n2_SystemParams.html")
print(psp)