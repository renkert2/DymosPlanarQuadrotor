# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""
import os
import dymos as dm
import openmdao.api as om
import numpy as np
import pickle

import SUPPORT_FUNCTIONS.plotting as my_plt # Just to get the default formatting
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import SUPPORT_FUNCTIONS.timing as timing
import Constraints as C
import Problems as P
import Recorders as R
import Trajectories as T
import PlanarSystem as ps

init.init_output(__file__, dirname="Output")

input_opt_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJ_STEP", "InputOptimization", "Output")
reader = om.CaseReader(os.path.join(input_opt_path, "input_opt_cases.sql"))
input_opt_final = reader.get_case("input_opt_final")

time, trajdat = T.getReferenceTraj(input_opt_final)
tx = dm.GaussLobatto(num_segments=20, compressed=True)
#tx = dm.Radau(num_segments=20, compressed=True)
traj = T.Track(time, trajdat["x_T"], trajdat["y_T"], trajdat["v_x_T"], trajdat["v_y_T"], trajdat["a_x_T"], trajdat["a_y_T"], trajdat["theta_T"], trajdat["omega_T"], tx=tx)
cons = C.ConstraintSet() # Create an empty constraint set
#cons.add(C.BatteryCurrent()) # for multiple phases
#cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)
cp = model.controller_params
cp["k_p_r"].opt = True
cp["k_p_r"].lb = 0.5
cp["k_p_r"].ub = 10

# cp["k_d_r"].opt = True
# cp["k_d_r"].lb = 0.1
# cp["k_d_r"].ub = 10

# cp["k_p_theta"].opt = True
# cp["k_p_theta"].lb = 0.1
# cp["k_p_theta"].ub = 10

# cp["k_d_theta"].opt = True
# cp["k_d_theta"].lb = 0.1
# cp["k_d_theta"].ub = 10

#%%
rec = R.Recorder(name="controller_opt_cases.sql")
driver = om.ScipyOptimizeDriver(optimizer="SLSQP")
prob = P.Problem(model=model, traj = traj, planar_recorder=rec, driver=driver)
prob.driver.declare_coloring()
prob.driver.options["maxiter"] = 100

driver.recording_options['includes'] = ['*']
driver.recording_options['excludes'] = []
driver.recording_options['record_objectives'] = True
driver.recording_options['record_constraints'] = True
driver.recording_options['record_desvars'] = True
driver.recording_options['record_inputs'] = True
driver.recording_options['record_outputs'] = True
driver.recording_options['record_residuals'] = True
prob.setup()
prob.init_vals()

#%% Initialize Values
nom_sim_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJFB_STEP", "TRAJFB_STEP_XY", "NominalSimulation", "Output")

reader = om.CaseReader(os.path.join(nom_sim_path, "nominal_sim_cases.sql"))
nom_sim_case = reader.get_case("nominal_sim_final")
prob.load_case(nom_sim_case)

with open(os.path.join(nom_sim_path, "pv_ctrl.pickle"), 'rb') as f:
    pv_ctrl_init = pickle.load(f)
    
for p in model.controller_params:
    p.load_val(pv_ctrl_init)

#%% Reporting
#prob.run_model()
#prob.driver.scaling_report()

#%%
prob.run("controller_opt")

prob.cleanup_all()

