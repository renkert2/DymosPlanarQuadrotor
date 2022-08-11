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
     
     def __init__(self, tx=None, sim_mode=False, include_controller=False, sim_args={"times_per_seg":20}):
         self.tx = tx # Problem transcription  
         self.sim_mode = sim_mode
         self.include_controller = include_controller
         phases = self.init_phases()
         super().__init__(phases, include_controller=include_controller)
         super().init_vars()
         
         self._sim_args = sim_args
     
     def init_phases(self):
        if "solve_segments" in self.tx.options:
           ss = self.tx.options["solve_segments"]
           if ss != False:
               if not self.sim_mode:
                   raise Exception("sim_mode=True required to forward solve the model.")
        elif isinstance(self.tx, dm.ExplicitShooting):
           if not self.sim_mode:
               raise Exception("sim_mode=True required for ExplicitShooting transcription")
        
        ### Implement Rest of Code in Subclasses ### 
        # Returns phases to be added to trajectory
        
        phases = []
        return phases

     def init_vals(self, prob):
         pass
     
     def simprob(self):
         return SimProblem(self, **self._sim_args)
     
     def refine(self, prob, refine_method = "hp", refine_iteration_limit = 0, **phase_kwargs):
         raise Exception("Not Implented")
         #TODO
         # for phase in self._phases.values():
         #     phase.set_refine_options(refine=True, **phase_kwargs)
         # failed = _refine_iter(prob, refine_iteration_limit, refine_method)
         
         # return prob.model.traj
        
### Trajectories ###
class Step(PlanarTrajectory):
    def __init__(self, tx=dm.GaussLobatto(num_segments=25, compressed=True), **kwargs):
        
        self.x_init=0
        self.y_init=0    
        
        self.x_des = 10
        self.y_des = 10
        
        self.time = 10
        
        super().__init__(tx=tx, **kwargs)

    def init_phases(self):
        super().init_phases()
        
        def pos_margin(p, margin):
            # Takes a list of positions and returns the min and the max with a padded boundary
            p_max = max(p)
            p_min = min(p)
            d = margin*(p_max - p_min)
            return (p_min - d, p_max + d)
        
        (self.x_lb, self.x_ub) = pos_margin([self.x_init, self.x_des], 0.1)
        (self.y_lb, self.y_ub) = pos_margin([self.y_init, self.y_des], 0.1)

        phase = ps.PlanarSystemDynamicPhase(transcription=self.tx, include_controller=self.include_controller)
        phase.init_vars()
        
        if self.sim_mode:
            fi=True
            ff=False
            ft = True
        else:
            fi = True
            ff = True
            ft = False
        
        # Set up States and Inputs as Optimization Variables
        phase.set_time_options(fix_initial=True, fix_duration=ft, initial_val=0, duration_bounds=(self.time/20, self.time*2), duration_ref0=1, duration_ref=self.time)
        
        phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=fi, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
        phase.set_state_options("PT_x2", fix_initial=fi, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options("PT_x3", fix_initial=fi, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options('BM_v_x', fix_initial=fi, fix_final=ff)
        phase.set_state_options('BM_v_y', fix_initial=fi, fix_final=ff)
        phase.set_state_options('BM_x', fix_initial=fi, fix_final=ff, lower=self.x_lb, ref0=self.x_lb, upper=self.x_ub, ref=self.x_ub)
        phase.set_state_options('BM_y', fix_initial=fi, fix_final=ff, lower=self.y_lb, ref0=self.y_lb, upper=self.y_ub, ref=self.y_ub)
        phase.set_state_options('BM_omega', fix_initial=fi, fix_final=ff)
        phase.set_state_options('BM_theta', fix_initial=fi, fix_final=ff, lower=-np.pi/2, ref0=-np.pi/2, upper=np.pi/2, ref=np.pi/2)
        if self.include_controller:
            phase.set_state_options("CTRL_e_omega_1_I", val=0, fix_initial=True, fix_final=False)
            phase.set_state_options("CTRL_e_omega_2_I", val=0, fix_initial=True, fix_final=False)
        
        if not self.include_controller:
            opt_in = not self.sim_mode
            phase.set_control_options("PT_u1", lower=0, upper=1, opt=opt_in, ref0=0.0, ref=1)
            phase.set_control_options("PT_u2", lower=0, upper=1, opt=opt_in, ref0=0.0, ref=1)
            
        if not self.sim_mode:
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
        prob.set_val(f'{name}.phase0.t_duration', self.time)
                
        prob.set_val(f'{name}.phase0.states:PT_x1', 1.0)
        
        phase = list(self._phases.values())[0]
        prob.set_val(f'{name}.phase0.states:PT_x2', phase.interp('PT_x2', ys=(0,1000)))
        prob.set_val(f'{name}.phase0.states:PT_x3', phase.interp('PT_x3', ys=(0,1000)))
        prob.set_val(f'{name}.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=[0, self.x_des/self.time]))
        prob.set_val(f'{name}.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=[0, self.y_des/self.time]))
        prob.set_val(f'{name}.phase0.states:BM_x', phase.interp('BM_x', ys=[0, self.x_des]))
        prob.set_val(f'{name}.phase0.states:BM_y', phase.interp('BM_y', ys=[0, self.y_des]))
        prob.set_val(f'{name}.phase0.states:BM_omega', phase.interp('BM_omega', ys=[0, 0]))
        prob.set_val(f'{name}.phase0.states:BM_theta', phase.interp('BM_theta', ys=[0, 0]))
        
        if self.include_controller:
            prob.set_val(f'{name}.phase0.controls:CTRL_x_T', phase.interp('CTRL_x_T', ys=[0, self.x_des]))
            prob.set_val(f'{name}.phase0.controls:CTRL_y_T', phase.interp('CTRL_y_T', ys=[0, self.y_des]))
            prob.set_val(f'{name}.phase0.controls:CTRL_v_x_T', phase.interp('CTRL_v_x_T', ys=[self.x_des/self.time, self.x_des/self.time]))
            prob.set_val(f'{name}.phase0.controls:CTRL_v_y_T', phase.interp('CTRL_v_y_T', ys=[self.y_des/self.time, self.y_des/self.time]))
            prob.set_val(f'{name}.phase0.controls:CTRL_a_x_T', 0)
            prob.set_val(f'{name}.phase0.controls:CTRL_a_y_T', 0)
        else:
            prob.set_val(f'{name}.phase0.controls:PT_u1', 0.5)
            prob.set_val(f'{name}.phase0.controls:PT_u2', 0.5)
        
class Mission_1(PlanarTrajectory):
    def __init__(self, tx=dm.GaussLobatto(num_segments=10, compressed=True), **kwargs):
        
        self.waypoints = ((0,0), (5,(5,7)), (15,2), (10,2), ((9,11),10), (10,12))
        
        self.duration_vals = None
        self.initial_vals = None
                        
        super().__init__(tx=tx, **kwargs)
                
        
    def init_phases(self):
        super().init_phases()
        
        # Phase Dependent Parameters
        duration_bounds = [ # Duration bounds for each phase
            (0.5,10),
            (0.5,10),
            (0.1,10),
            (0.5,10),
            (0.01, 10)
            ]
        duration_vals = [np.mean(x) for x in duration_bounds]
        self.duration_vals = duration_vals
        
        initial_bounds = [(0,0)]
        ib_l = 0
        ib_u = 0
        for db in duration_bounds[:-1]:
            ib_l += db[0]
            ib_u += db[1]
            initial_bounds.append((ib_l, ib_u))
        initial_vals = [np.mean(x) for x in initial_bounds]
        self.initial_vals = initial_vals
        
        x_bounds = [
            (-1,5),
            (5,20),
            (5,20),
            (5,20),
            (5,20)
            ]
        
        y_bounds = [
            (0,10),
            (0,10),
            (0,10),
            (0,15),
            (10,15)
            ]
        
        # Fixed x-position states
        fi_x = [True, True, True, True, False]
        ff_x = [False, False, False, False, True]
        
        # Fixed y-position states
        fi_y = [True, False, True, True, True]
        ff_y = [False,False, False, False, True]
        
        # Fixed stationary (zero velocity) states
        fi_all = [True, False, True, False, False]
        ff_all = [False, False, False, False, True]
        
        phases = []
        phase_range = range(len(self.waypoints) - 1)
        for i in phase_range:
            phase = ps.PlanarSystemDynamicPhase(transcription=self.tx)
            phase.init_vars()
            
            # Set up phase Time
            if i == 0:
                fi = True
            else:
                fi = False
            phase.set_time_options(fix_initial=fi, 
                                   initial_val = initial_vals[i],
                                   initial_bounds = initial_bounds[i],
                                   initial_ref0 = initial_bounds[i][0],
                                   initial_ref = initial_bounds[i][1],
                                   
                                   duration_val = duration_vals[i],
                                   duration_bounds=duration_bounds[i], 
                                   duration_ref0=duration_bounds[i][0], 
                                   duration_ref=duration_bounds[i][1],
                                   )
                    
            # Setup Inputs
            phase.set_control_options("PT_u1", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
            phase.set_control_options("PT_u2", lower=0, upper=1, opt=True, ref0=0.0, ref=1)
            
            # Setup phase Powertrain States
            if i == 0:
                fi = True
            else:
                fi = False
            phase.set_state_options("PT_x1", fix_initial=fi, val=1, lower=0, upper=1,  ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
            phase.set_state_options("PT_x2", fix_initial=fi, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
            phase.set_state_options("PT_x3", fix_initial=fi, lower=0, upper=5000, ref0=0.0, ref=5000) # Scaling ref=5000 has the largest impact on the solution
            
            # Setup Body States
            phase.set_state_options('BM_v_x', fix_initial=fi_all[i], fix_final=ff_all[i])
            phase.set_state_options('BM_v_y', fix_initial=fi_all[i], fix_final=ff_all[i])
            phase.set_state_options('BM_x', fix_initial=fi_x[i], fix_final=ff_x[i], lower=x_bounds[i][0], ref0=x_bounds[i][0], upper=x_bounds[i][1], ref=x_bounds[i][1])
            phase.set_state_options('BM_y', fix_initial=fi_y[i], fix_final=ff_y[i], lower=y_bounds[i][0], ref0=y_bounds[i][0], upper=y_bounds[i][1], ref=y_bounds[i][1])
            phase.set_state_options('BM_omega', fix_initial=fi_all[i], fix_final=ff_all[i])
            phase.set_state_options('BM_theta', fix_initial=fi_all[i], fix_final=ff_all[i], lower=-np.pi/2, ref0=-np.pi/2, upper=np.pi/2, ref=np.pi/2)
            
            # Setup Constraints
            if i == 0:
                bnd = self.waypoints[i+1][1]
                phase.add_boundary_constraint("BM_y", loc='final',lower=bnd[0],upper=bnd[1],ref0=bnd[0],ref=bnd[1])
            elif i == 3:
                bnd = self.waypoints[i+1][0]
                phase.add_boundary_constraint("BM_x", loc='final',lower=bnd[0],upper=bnd[1],ref0=bnd[0],ref=bnd[1])
                

            # Minimize time at the end of the phase
            if i == phase_range[-1]:
                phase.add_objective('time', loc='final')
                
            phases.append(phase)
        return phases
    
    def init_vals(self, prob, name="traj"):
        # Set Initial Values
        for (i, (pn, p)) in enumerate(self._phases.items()):
            prob.set_val(f'{name}.{pn}.t_initial', self.initial_vals[i])
            prob.set_val(f'{name}.{pn}.t_duration', self.duration_vals[i])
            
            prob.set_val(f'{name}.{pn}.controls:PT_u1', 0.5)
            prob.set_val(f'{name}.{pn}.controls:PT_u2', 0.5)
            
            prob.set_val(f'{name}.{pn}.states:PT_x1', 1.0)
            prob.set_val(f'{name}.{pn}.states:PT_x2', 1000)
            prob.set_val(f'{name}.{pn}.states:PT_x3', 1000)
                        
            reduce_waypoints = lambda wp : [np.mean(x) if hasattr(x, "__len__") else x for x in wp]
            pnt_1 = reduce_waypoints(self.waypoints[i])
            pnt_2 = reduce_waypoints(self.waypoints[i+1])
            
            prob.set_val(f'{name}.{pn}.states:BM_x', p.interp('BM_x', ys=[pnt_1[0], pnt_2[0]]))
            prob.set_val(f'{name}.{pn}.states:BM_y', p.interp('BM_y', ys=[pnt_1[1], pnt_2[1]]))
            
            prob.set_val(f'{name}.{pn}.states:BM_v_x', 0)
            prob.set_val(f'{name}.{pn}.states:BM_v_y', 0)
            
            prob.set_val(f'{name}.{pn}.states:BM_omega', 0)
            prob.set_val(f'{name}.{pn}.states:BM_theta', 0)
            
class Track(PlanarTrajectory):
    def __init__(self, time, x_T, y_T, v_x_T, v_y_T, a_x_T, a_y_T, theta_T, omega_T, tx=dm.GaussLobatto(num_segments=25, compressed=True), **kwargs):        
        self.time = time
        self.x_T = x_T
        self.y_T = y_T
        self.v_x_T = v_x_T
        self.v_y_T = v_y_T
        self.a_x_T = a_x_T
        self.a_y_T = a_y_T
        
        # The following are only used for scaling, not as actual inputs
        self.theta_T = theta_T
        self.omega_T = omega_T
        
        super().__init__(tx=tx, sim_mode=True, include_controller=True, **kwargs)
        
    def init_phases(self):
        super().init_phases()
        phase = ps.PlanarSystemDynamicPhase(transcription=self.tx, include_controller=True)
        phase.init_vars()
        
        def pos_margin(p, margin):
            # Takes a list of positions and returns the min and the max with a padded boundary
            p_max = max(p)
            p_min = min(p)
            d = margin*(p_max - p_min)
            return (p_min - d, p_max + d)
        
        (x_lb, x_ub) = pos_margin(self.x_T, 2)
        (y_lb, y_ub) = pos_margin(self.y_T, 2)
        
        (v_x_lb, v_x_ub) = pos_margin(self.v_x_T, 2)
        (v_y_lb, v_y_ub) = pos_margin(self.v_y_T, 2)
        
        (theta_lb, theta_ub) = pos_margin(self.theta_T, 2)
        (omega_lb, omega_ub) = pos_margin(self.omega_T, 2)
        
        PT_omega_lb = -2000
        PT_omega_ub = 2000
        
        PT_omega_I_lb = PT_omega_lb*self.time[-1]
        PT_omega_I_ub = PT_omega_ub*self.time[-1]
        
        fi=True
        ff=False
        ft = True
        
        # Set up States and Inputs as Optimization Variables
        phase.set_time_options(fix_initial=fi, fix_duration=ft, initial_val=0, duration_ref=self.time[-1])
        
        phase.set_state_options("PT_x1", val=1, lower=0, upper=1, fix_initial=fi, ref0 = 0, ref=1) # Fix Battery State of Charge Initial State to 1
        phase.set_state_options("PT_x2", fix_initial=fi, ref0=0.0, ref=PT_omega_ub, lower=PT_omega_lb, upper=PT_omega_ub) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options("PT_x3", fix_initial=fi, ref0=0.0, ref=PT_omega_ub, lower=PT_omega_lb, upper=PT_omega_ub) # Scaling ref=5000 has the largest impact on the solution
        phase.set_state_options('BM_v_x', fix_initial=fi, fix_final=ff, ref0=v_x_lb, ref=v_x_ub, lower=v_x_lb, upper=v_x_ub)
        phase.set_state_options('BM_v_y', fix_initial=fi, fix_final=ff, ref0=v_y_lb, ref=v_y_ub, lower=v_y_lb, upper=v_y_ub)
        phase.set_state_options('BM_x', fix_initial=fi, fix_final=ff, ref0=x_lb, ref=x_ub, lower=x_lb, upper=x_ub)
        phase.set_state_options('BM_y', fix_initial=fi, fix_final=ff, ref0=y_lb, ref=y_ub, lower=y_lb, upper=y_ub)
        phase.set_state_options('BM_omega', fix_initial=fi, fix_final=ff, ref0=omega_lb, ref=omega_ub, lower=omega_lb, upper=omega_ub)
        phase.set_state_options('BM_theta', fix_initial=fi, fix_final=ff, ref0=theta_lb, ref=theta_ub, lower=theta_lb, upper=theta_ub)
        phase.set_state_options("CTRL_e_omega_1_I", val=0, fix_initial=fi, fix_final=ff, ref0=0.0, ref=100, lower=PT_omega_I_lb, upper=PT_omega_I_ub)
        phase.set_state_options("CTRL_e_omega_2_I", val=0, fix_initial=fi, fix_final=ff, ref0=0.0, ref=100, lower=PT_omega_I_lb, upper=PT_omega_I_ub)
        
        e_T_I_ref = ((x_ub-x_lb)**2 + (y_ub-y_lb)**2)/4
        phase.set_state_options("CTRL_e_T_I", val=0, lower=0, fix_initial=fi, fix_final = ff, ref=e_T_I_ref)
        
        # Minimize tracking error
        phase.add_objective('CTRL_e_T_I', loc='final', ref=e_T_I_ref)
        
        return phase
    
    def init_vals(self, prob, name="traj"):
        # Set Initial Values
        prob.set_val(f'{name}.phase0.t_initial', 0.0)
        prob.set_val(f'{name}.phase0.t_duration', self.time[-1])
                
        prob.set_val(f'{name}.phase0.states:PT_x1', 1.0)
        
        interp_kwargs = {"xs":self.time, "kind":"cubic"}
        phase = list(self._phases.values())[0]
        prob.set_val(f'{name}.phase0.states:PT_x2', 0)
        prob.set_val(f'{name}.phase0.states:PT_x3', 0)
        prob.set_val(f'{name}.phase0.states:BM_v_x', phase.interp('BM_v_x', ys=self.v_x_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.states:BM_v_y', phase.interp('BM_v_y', ys=self.v_y_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.states:BM_x', phase.interp('BM_x', ys=self.x_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.states:BM_y', phase.interp('BM_y', ys=self.y_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.states:BM_omega', 0)
        prob.set_val(f'{name}.phase0.states:BM_theta', 0)

        prob.set_val(f'{name}.phase0.controls:CTRL_x_T', phase.interp('CTRL_x_T', ys=self.x_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.controls:CTRL_y_T', phase.interp('CTRL_y_T', ys=self.y_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.controls:CTRL_v_x_T', phase.interp('CTRL_v_x_T', ys=self.v_x_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.controls:CTRL_v_y_T', phase.interp('CTRL_v_y_T', ys=self.v_y_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.controls:CTRL_a_x_T', phase.interp('CTRL_a_x_T', ys=self.a_x_T, **interp_kwargs))
        prob.set_val(f'{name}.phase0.controls:CTRL_a_y_T', phase.interp('CTRL_a_y_T', ys=self.a_y_T, **interp_kwargs))

def getReferenceTraj(case, phases=["phase0"]):
    #TODO: Implement multiple phases
    time = case.get_val("traj.phases.phase0.timeseries.time")
    time = np.ndarray.flatten(time)
    time,I = np.unique(time, return_index=True)
    trajdat = {}
    for n,t in (("x_T", "states:BM_x"), ("y_T", "states:BM_y"), ("v_x_T", "states:BM_v_x"), ("v_y_T", "states:BM_v_y"), ("a_x_T", "state_rates:BM_v_x"),  ("a_y_T", "state_rates:BM_v_y"), ("theta_T", "states:BM_theta"), ("omega_T", "states:BM_omega")):
        trajdat[n] = np.ndarray.flatten(case.get_val(f"traj.phases.phase0.timeseries.{t}"))[I]
    
    return (time, trajdat)