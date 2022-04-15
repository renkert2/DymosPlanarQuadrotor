# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 15:39:09 2022

@author: renkert2
"""

import PlanarSystem as ps
import dymos as dm
import openmdao.api as om
import numpy as np
from dymos.grid_refinement.refinement import _refine_iter
from dymos.utils.misc import _unspecified

class SimProblem(om.Problem):
    def __init__(self, traj, times_per_seg=10, method=_unspecified, atol=_unspecified, rtol=_unspecified, first_step=_unspecified, max_step=_unspecified):
       
       sim_traj = dm.Trajectory(sim_mode=True)
    
       for name, phs in traj._phases.items():
           sim_phs = phs.get_simulation_phase(times_per_seg=times_per_seg, method=method, atol=atol, rtol=rtol, first_step=first_step, max_step=max_step)
           sim_traj.add_phase(name, sim_phs)
     
       sim_traj.parameter_options.update(traj.parameter_options)
     
       super().__init__(model=om.Group())
     
       traj_name = traj.name if traj.name else 'sim_traj'
       self.model.add_subsystem(traj_name, sim_traj)
       
       self._sim_traj = sim_traj
       self._traj_name = traj_name
       self._traj = traj
    
    def add_recorder(self, rec=om.SqliteRecorder("sim_cases.sql")):
        super().add_recorder(rec)
        # record_inputs is needed to capture potential input parameters that aren't connected
        self.recording_options['record_inputs'] = True
        # record_outputs is need to capture the timeseries outputs
        self.recording_options['record_outputs'] = True
    
    def simulate(self):   
        sim_traj = self._sim_traj
        traj_name = self._traj_name
        traj = self._traj
    
        # Assign trajectory parameter values
        param_names = [key for key in traj.parameter_options.keys()]
        for name in param_names:
            prom_path = f'{traj.name}.parameters:{name}'
            src = traj.get_source(prom_path)
     
            # We use this private function to grab the correctly sized variable from the
            # auto_ivc source.
            val = traj._abs_get_val(src, False, None, 'nonlinear', 'output', False, from_root=True)
            sim_prob_prom_path = f'{traj_name}.parameters:{name}'
            self[sim_prob_prom_path][...] = val
     
        for phase_name, phs in sim_traj._phases.items():
            skip_params = set(param_names)
            for name in param_names:
                targets = traj.parameter_options[name]['targets']
                if targets and phase_name in targets:
                    targets_phase = targets[phase_name]
                    if targets_phase is not None:
                        if isinstance(targets_phase, str):
                            targets_phase = [targets_phase]
                        skip_params = skip_params.union(targets_phase)
     
            phs.initialize_values_from_phase(self, traj._phases[phase_name],
                                             phase_path=traj_name,
                                             skip_params=skip_params)
     
        print('\nSimulating trajectory {0}'.format(traj.pathname))
        self.run_model()
        print('Done simulating trajectory {0}'.format(traj.pathname))
 
        return self

class PlanarTrajectory(ps.PlanarSystemDynamicTraj): 
     # Superclass for specific optimal control trajectories that we want the vehicle to take.
     # We want all options, etc to be constant so that the trajectories are uniform across all problems
     
     def __init__(self, tx=None, sim_mode=False, sim_args={"times_per_seg":20}):
         self.tx = tx # Problem transcription  
         self.sim_mode = sim_mode
         phases = self.init_phases()
         super().__init__(phases)
         super().init_vars()
         
         self._sim_args = sim_args
     
     def init_phases(self):
         pass

     def init_vals(self, prob):
         pass
     
     def simprob(self):
         return SimProblem(self, **self._sim_args)
     
     def refine(self, prob, refine_method = "hp", refine_iteration_limit = 0, **phase_kwargs):
         for phase in self._phases.values():
             phase.set_refine_options(refine=True, **phase_kwargs)
         failed = _refine_iter(prob, refine_iteration_limit, refine_method)
         
         return prob.model.traj
        
### Trajectories ###
class Step(PlanarTrajectory):
    def __init__(self, tx=dm.GaussLobatto(num_segments=25, compressed=True), **kwargs):
        
        self.x_init=0
        self.y_init=0    
        
        self.x_des = 10
        self.y_des = 10
        
        super().__init__(tx=tx, **kwargs)

    def init_phases(self):
        def pos_margin(p, margin):
            # Takes a list of positions and returns the min and the max with a padded boundary
            p_max = max(p)
            p_min = min(p)
            d = margin*(p_max - p_min)
            return (p_min - d, p_max + d)
        
        (self.x_lb, self.x_ub) = pos_margin([self.x_init, self.x_des], 0.1)
        (self.y_lb, self.y_ub) = pos_margin([self.y_init, self.y_des], 0.1)

        phase = ps.PlanarSystemDynamicPhase(transcription=self.tx)
        phase.init_vars()
        
        if "solve_segments" in self.tx.options:
            ss = self.tx.options["solve_segments"]
            if ss != False:
                if not self.sim_mode:
                    raise Exception("sim_mode=True required to forward solve the model.")
        elif isinstance(self.tx, dm.ExplicitShooting):
            if not self.sim_mode:
                raise Exception("sim_mode=True required for ExplicitShooting transcription")
        
        if self.sim_mode:
            fi=True
            ff=False
        else:
            fi = True
            ff = True
        
        # Set up States and Inputs as Optimization Variables
        phase.set_time_options(fix_initial=fi, initial_val=0, duration_bounds=(1, 20), duration_ref0=1, duration_ref=20)
        
        phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=fi, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
        phase.set_state_options("PT_x2", fix_initial=fi, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options("PT_x3", fix_initial=fi, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options('BM_v_x', fix_initial=fi, fix_final=ff)
        phase.set_state_options('BM_v_y', fix_initial=fi, fix_final=ff)
        phase.set_state_options('BM_x', fix_initial=fi, fix_final=ff, lower=self.x_lb, ref0=self.x_lb, upper=self.x_ub, ref=self.x_ub)
        phase.set_state_options('BM_y', fix_initial=fi, fix_final=ff, lower=self.y_lb, ref0=self.y_lb, upper=self.y_ub, ref=self.y_ub)
        phase.set_state_options('BM_omega', fix_initial=fi, fix_final=ff)
        phase.set_state_options('BM_theta', fix_initial=fi, fix_final=ff, lower=-np.pi/2, ref0=-np.pi/2, upper=np.pi/2, ref=np.pi/2)
        
        phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
        phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
        
        phase.add_boundary_constraint('PT.x2_dot', loc='final', shape=(1,), equals=0) # Shape may need to change to (nn,)
        phase.add_boundary_constraint('PT.x3_dot', loc='final', shape=(1,), equals=0)
        phase.add_boundary_constraint('BM.v_y_dot', loc='final', shape=(1,), equals=0)
        phase.add_boundary_constraint('BM.omega_dot', loc='final', shape=(1,), equals=0)
        
        # Minimize time at the end of the phase
        phase.add_objective('time', loc='final')
        return phase
    
    def init_vals(self, prob, name="traj"):
        # Set Initial Values
        prob.set_val(f'{name}.phase0.t_initial', 0.0)
        prob.set_val(f'{name}.phase0.t_duration', 10.0)
        
        prob.set_val(f'{name}.phase0.controls:PT_u1', 0.5)
        prob.set_val(f'{name}.phase0.controls:PT_u2', 0.5)
        
        prob.set_val(f'{name}.phase0.states:PT_x1', 1.0)
        
        phase = list(self._phases.values())[0]
        prob.set_val(f'{name}.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
        prob.set_val(f'{name}.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
        prob.set_val(f'{name}.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_x', phase.interp('BM_x', ys=[0, 10]))
        prob.set_val(f'{name}.phase0.states:BM_y', phase.interp('BM_y', ys=[0, 10]))
        prob.set_val(f'{name}.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))
        
         