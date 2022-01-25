# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 08:36:58 2021

@author: renkert2
"""

import os
os.chdir(os.path.join(os.path.dirname(__file__), '..', '..'))
import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import time
import SUPPORT_FUNCTIONS.plotting as plt
import warnings


def main():
    os.chdir(os.path.dirname(__file__))
    if not os.path.isdir("Output"):
        os.mkdir("Output")
    os.chdir("Output")
    
    warnings.filterwarnings('ignore', category=om.UnitsWarning)

    # The goal of this study is to compare the performance of symbolically substituted
    # algebraic states with numerically calculated algebraic states.  

    nn = 20
    tx = dm.Radau(num_segments=nn, compressed=False)
    
    model_type = "DAE" # Ran faster in input optimization test, may be more robust with simpler Jacobians
    phase = ps.PlanarSystemDynamicPhase(transcription=tx, model_kwargs={"ModelType":model_type})
    phase.init_vars()
    setup_phase(phase)
    
    planar_model.add_design_var('N_s__Battery', lower=2, upper=6, ref0=2, ref=6)
    planar_model.add_design_var('Q__Battery', lower=500, upper=6000, ref0=500, ref=6000)
    
    prob, traj = setup_prob(phase)
    set_vals(prob,phase)
    out = run(prob, traj)
    data[model_type] = out
        
    return data

def setup_phase(phase):
    # Set up States and Inputs as Optimization Variables
    phase.set_time_options(fix_initial=True, initial_val=0, duration_bounds=(0.001, 50))
    
    phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
    phase.set_state_options("PT_x2", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
    phase.set_state_options("PT_x3", fix_initial=True, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
    phase.set_state_options('BM_v_x', fix_initial=True, fix_final=True)
    phase.set_state_options('BM_v_y', fix_initial=True, fix_final=True)
    phase.set_state_options('BM_x', fix_initial=True, fix_final=True)
    phase.set_state_options('BM_y', fix_initial=True, fix_final=True)
    phase.set_state_options('BM_omega', fix_initial=True, fix_final=True)
    phase.set_state_options('BM_theta', fix_initial=True, fix_final=True)
    
    phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
    phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
    
    phase.add_boundary_constraint('PT.x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
    phase.add_boundary_constraint('PT.x3_dot', loc='final', shape=(1,), equals=0)
    phase.add_boundary_constraint('BM.v_y_dot', loc='final', shape=(1,), equals=0, units='m/s**2')
    phase.add_boundary_constraint('BM.omega_dot', loc='final', shape=(1,), equals=0, units='rad/s**2')
    
    # Minimize time at the end of the phase
    phase.add_objective('time', loc='final')
    
    return phase

def setup_prob(phase):
    prob = om.Problem(model=om.Group())
    prob.driver = om.ScipyOptimizeDriver()
    traj = dm.Trajectory()
    traj.add_phase('phase0', phase)
    
    prob.model.add_subsystem('traj', traj)
    prob.model.linear_solver = om.DirectSolver() # I'm not sure why we need this
    
    prob.setup()
    
    return prob, traj

def set_vals(prob, phase):
    # Set Initial Values
    prob.set_val('traj.phase0.t_initial', 0.0)
    prob.set_val('traj.phase0.t_duration', 10.0)
    
    prob.set_val('traj.phase0.controls:PT_u1', 0.5)
    prob.set_val('traj.phase0.controls:PT_u2', 0.5)
    
    prob.set_val('traj.phase0.states:PT_x1', 1.0)
    prob.set_val('traj.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
    prob.set_val('traj.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
    prob.set_val('traj.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
    prob.set_val('traj.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
    prob.set_val('traj.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 10]))
    prob.set_val('traj.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 10]))
    prob.set_val('traj.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
    prob.set_val('traj.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))
    
    return prob

def run(prob, traj):
    #
    # Run the Optimization Problem
    #
    tic = time.perf_counter()
    dm.run_problem(prob)
    toc = time.perf_counter()
    run_time = toc-tic
    print(f"Problem solved in {run_time:0.4f} seconds")
    
    tic = time.perf_counter()
    sim_out = traj.simulate(times_per_seg=50)
    toc = time.perf_counter()
    sim_time = toc-tic
    print(f"Simulation ran in {sim_time:0.4f} seconds")
    
    return {"RunTime":run_time, "SimTime":sim_time}
#%% Plots

# plt.subplots(sim_out, prob, path='traj.phase0.timeseries',
#              vars=[f"states:{x}" for x in  ['BM_x', 'BM_y', 'BM_theta']] + [f"controls:{x}" for x in  ['PT_u1', 'PT_u2']],
#              labels=['$x$', '$y$', r'$\theta$', "$u_1$", "$u_2$"], 
#              title="Planar Quadrotor Input Optimization", save=True)

if __name__ == "__main__":
    data = main()
