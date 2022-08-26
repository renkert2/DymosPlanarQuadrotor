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

import GraphTools_Phil_V2.OpenMDAO.PARAMS.Param as Param
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
tx = dm.GaussLobatto(num_segments=30, compressed=True)
#tx = dm.Radau(num_segments=20, compressed=True)
traj = T.Track(time, trajdat["x_T"], trajdat["y_T"], trajdat["v_x_T"], trajdat["v_y_T"], trajdat["a_x_T"], trajdat["a_y_T"], trajdat["theta_T"], trajdat["omega_T"], tx=tx)
cons = C.ConstraintSet() # Create an empty constraint set
#cons.add(C.BatteryCurrent()) # for multiple phases
#cons.add(C.InverterCurrent())
model = ps.PlanarSystemModel(traj, cons=cons)

#TODO: Implement as system constraint somehow
model.add_constraint("traj.phase0.rhs_col.CTRL.u_1_delta", lower=-0.5, upper=0.5)
model.add_constraint("traj.phase0.rhs_col.CTRL.u_2_delta", lower=-0.5, upper=0.5)


cp = model.controller_params

cp["k_p_r"].opt = False
cp["k_p_r"].lb = 0.0
cp["k_p_r"].ub = 2

cp["k_d_r_x"].opt = True
cp["k_d_r_x"].lb = 0.0
cp["k_d_r_x"].ub = 50

cp["k_d_r_y"].opt = True
cp["k_d_r_y"].lb = 0.0
cp["k_d_r_y"].ub = 50

cp["k_p_theta"].opt = True
cp["k_p_theta"].lb = 0.0
cp["k_p_theta"].ub = 2

cp["k_d_theta"].opt = True
cp["k_d_theta"].lb = 0.0
cp["k_d_theta"].ub = 2

#%%
rec = R.Recorder(name="controller_opt_cases.sql")
driver = om.pyOptSparseDriver()

driver.options['optimizer'] = "IPOPT"
driver.opt_settings["print_level"] = 5
driver.opt_settings["max_iter"] = 3000
driver.opt_settings["tol"] = 1e-8 # Default: 1e-8

# NLP
#Xdriver.opt_settings['bound_relax_factor'] = 0.00 # If nonzero, relaxes constraints.

# Tried these: Newton solver fails to converge when evaluating h
# driver.opt_settings['nlp_scaling_method'] = 'gradient-based' # default: user-specified
# driver.opt_settings['nlp_scaling_max_gradient'] = 100.0
# driver.opt_settings['constr_mult_init_max'] = 1000.0

# Mu Adaptation
#driver.opt_settings['adaptive_mu_globalization] = 'never-monotone-mode' #default:obj-sontr-filter
#driver.opt_settings['mu_strategy'] = 'adaptive' #default:'monotone'

# Line Search
#driver.opt_settings['alpha_red_factor'] = 0.5 #default=0.5, between 0 and 1
#driver.opt_settings['alpha_for_y'] = 'safer-min-dual-infeas' #default='primal'
#driver.opt_settings['corrector_type'] = 'affine' # also try 'primal-dual'; only applies when mu_strategy is adaptive. default='none'

# Restoration
#driver.opt_settings['expect_infeasible_problem"] = 'yes' #default='no'
#driver.opt_settings['start_with_resto'] = 'yes' #default='no'


# driver.options['optimizer'] = "SLSQP"
# driver.opt_settings["IPRINT"] = 1
# driver.opt_settings["MAXIT"] = 500

driver.recording_options['includes'] = ['*']
driver.recording_options['excludes'] = []
driver.recording_options['record_objectives'] = True
driver.recording_options['record_constraints'] = True
driver.recording_options['record_desvars'] = True
driver.recording_options['record_inputs'] = True
driver.recording_options['record_outputs'] = True
driver.recording_options['record_residuals'] = True

prob = P.Problem(model=model, traj = traj, planar_recorder=rec, driver=driver)
prob.driver.declare_coloring()

prob.setup()
prob.init_vals()

#%% Initialize Values
nom_sim_path = os.path.join(init.HOME_PATH, "STUDIES", "TRAJFB_STEP", "TRAJFB_STEP_XY", "NominalSimulation", "Output")

reader = om.CaseReader(os.path.join(nom_sim_path, "nominal_sim_cases.sql"))
nom_sim_case = reader.get_case("nominal_sim_final")
prob.load_case(nom_sim_case)

with open(os.path.join(nom_sim_path, "pv_ctrl.pickle"), 'rb') as f:
    pv_ctrl_init = Param.ParamValSet(pickle.load(f))
    
for p in model.controller_params:
    p.load_val(pv_ctrl_init)

#%% Reporting
#prob.run_model()
#prob.driver.scaling_report()

#%%
prob.run("controller_opt")
#prob.run_driver(case_prefix='controller_opt')

prob.cleanup_all()

