# -*- coding: utf-8 -*-
"""
Created on Sat Nov 20 13:16:51 2021

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import os
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
from BatterySurrogate import BatterySurrogate

p = om.Problem(model=om.Group())


p.model.add_subsystem('batt_surrogate', BatterySurrogate())


p.setup(force_alloc_complex=True)

p.run_model()
cpd = p.check_partials(method='cs', compact_print=True)