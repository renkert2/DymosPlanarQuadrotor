# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:39:09 2022

@author: renkert2
"""
import dymos as dm
import openmdao.api as om
import numpy as np
from tabulate import tabulate

from GraphTools_Phil_V2.OpenMDAO import Param as P

import SUPPORT_FUNCTIONS.support_funcs as funcs
import Recorders
import Trajectories
import PlanarSystem as ps

class Problem(om.Problem):
    def __init__(self, model = None, traj = None, sim=True, driver=om.ScipyOptimizeDriver(), planar_recorder=Recorders.Recorder(), **kwargs):
        super().__init__(model=model, **kwargs)
        self.planar_model = model
        self.driver = driver
        
        self.traj = traj
        
        self.sim_flag = sim
        self.sim_prob = None
        self.planar_recorder = planar_recorder
        
    def setup(self):
        if self.planar_recorder:        
            r = self.planar_recorder
            r.add_prob(self)
            r.add_driver(self.driver)
     
        super().setup()

        if self.sim_flag:
            sp = self.traj.simprob()
            
            if self.planar_recorder:
                r.add_sim_prob(sp)
            sp.setup()
            self.sim_prob = sp
        
    def init_vals(self):
        self.traj.init_vals(self)
        if self.sim_prob:
            #self.traj.init_vals(self.sim_prob)
            pass
    
    def run(self, desc="problem"):
        self.run_model(reset_iter_counts=True)
        
        if self.sim_flag:
            self.sim_prob.simulate()
        
        self.planar_recorder.record_all(f"{desc}_initial")
        
        self.run_driver(reset_iter_counts=True)
        
        if self.sim_flag:
            self.sim_prob.simulate()
        
        self.planar_recorder.record_all(f"{desc}_final")
        #self.planar_recorder.record_results()
        
    def list_problem_vars(self):
        super().list_problem_vars(desvar_opts=['lower', 'upper', 'ref', 'ref0'],
                       cons_opts=['lower', 'upper', 'ref', 'ref0'],
                       objs_opts=['ref', 'ref0'])
    
    def get_objective(self):
        for v in self.model.get_objectives().values():
            source = v["source"]
            indexer = v["indices"]
            return self.get_val(source, indices=indexer.flat())
        
    def cleanup_all(self):
        self.cleanup()
        self.sim_prob.cleanup()
        
    def fdiff(self, of, wrt, step_size=0.01):
        def to_paths(l):
            return [f"params.{x.strID}" if isinstance(x, P.Param) else x for x in l]
        of_paths = to_paths(of)
        wrt_paths = to_paths(wrt)
        
        def to_latex(l):
            return [x.latex() if hasattr(x, "latex") else x for x in l]
        of_latex = to_latex(of)
        wrt_latex = to_latex(wrt)
        
        # Modify dependency of params
        # - of's must be independent
        # - all surrogates downstream of the ofs must be be active
        
        def get(paths):
            x = np.zeros(len(paths))
            for (i,p) in enumerate(paths):
                val = self.get_val(p)
                if len(val) > 1:
                    val = val[-1] # Assume final value
                x[i] = funcs.scalarize(val)
            return x
        
        self.run_driver() # Get updated objective with nominal params
        
        F0 = get(of_paths)
        X0 = get(wrt_paths)
        print(f"Nominal F: {F0}, Nominal X: {X0}")
        
        Delta = step_size*X0 # Step Sizes in Unscaled space
        X = X0 + Delta
        
        grad_data = [] # list of (grad, grad_scaled) tuples
        for i,wrt_p in enumerate(wrt_paths):
            print(f"Stepping: {wrt_p}")
            
            print(f"New Value: {X[i]}; Nominal Value: {X0[i]}")
            self.set_val(wrt_p, val=X[i])
            
            self.run_driver()
            F = get(of_paths)
            
            delta_F = (F - F0) 
            grad = delta_F/Delta[i]
            grad_scaled = (X[i]*grad)/abs(F0)
            
            grad_data.append((grad, grad_scaled, F))
            
            print(f"Step Complete: delta_F={delta_F}, grad={grad}, grad_scaled={grad_scaled}")
            
            self.set_val(wrt_p, val=X0[i])
        
        # Latex Table Headers:
        lt_headers = ["Gradient", "Scaled Gradient"]
        # Process Vals:
        out_dict = {} # Format: out_dict[of][wrt][unscaled,scaled]
        latex_tables = {}
        for i,of_i in enumerate(of):
            D1 = {}

            lt_vals = []
            for j,wrt_j in enumerate(wrt):
                D2 = {}
                for k,s in enumerate(["unscaled", "scaled"]):
                    D2[s] = grad_data[j][k][i]
                D1[wrt_j] = D2
                
                # Record Vals for Latex # 
                lt_vals.append([wrt_latex[j], D2["unscaled"], D2["scaled"]])

            out_dict[of_i] = D1
            
            # Latex Tables
            lt_string = tabulate(lt_vals, headers=lt_headers, tablefmt="latex_raw")
            latex_tables[of_i] = lt_string
        
        return out_dict, latex_tables
    



### ARCHIVE ###
def ForwardSimulation():
    nn = 20
    tx = dm.GaussLobatto(num_segments=nn, solve_segments='forward')
    phase = ps.PlanarSystemDynamicPhase(transcription=tx)
    phase.init_vars()
    
    # Setup Dynamic Problem
    phase.set_time_options(fix_initial=True, fix_duration=True, initial_val=0, duration_val=5)
    
    phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=True, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
    phase.set_state_options("PT_x2", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
    phase.set_state_options("PT_x3", fix_initial=True, fix_final=False, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
    phase.set_state_options('BM_v_x', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_v_y', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_x', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_y', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_omega', fix_initial=True, fix_final=False)
    phase.set_state_options('BM_theta', fix_initial=True, fix_final=False)
    
    phase.set_control_options("PT_u1", val=1, opt=False)
    phase.set_control_options("PT_u2", val=1, opt=False)
    
    traj = ps.PlanarSystemDynamicTraj(phase)
    traj.init_vars()
    
    planar_model=ps.PlanarSystemModel(traj)

    prob = om.Problem(model=planar_model)
    prob.driver = om.ScipyOptimizeDriver()
    prob.model.linear_solver = om.DirectSolver()
    
    prob.setup()

    # Set Initial Values
    prob.set_val('traj.phase0.t_initial', 0.0)
    prob.set_val('traj.phase0.t_duration', 5.0)
    
    prob.set_val('traj.phase0.controls:PT_u1', 1)
    prob.set_val('traj.phase0.controls:PT_u2', 1)
    
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