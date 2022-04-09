# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 14:45:00 2022

@author: renkert2
"""

import numpy as np
import openmdao.api as om
import dymos as dm
import time
from openmdao.utils.array_utils import evenly_distrib_idxs


class VanderpolODE(om.ExplicitComponent):
    """intentionally slow version of vanderpol_ode for effects of demonstrating distributed component calculations

    MPI can run this component in multiple processes, distributing the calculation of derivatives.
    This code has a delay in it to simulate a longer computation. It should run faster with more processes.
    """

    def __init__(self, *args, **kwargs):
        self.progress_prints = False
        super().__init__(*args, **kwargs)

    def initialize(self):
        self.options.declare('num_nodes', types=int)
        self.options.declare('distrib', types=bool, default=False)

    def setup(self):
        nn = self.options['num_nodes']
        comm = self.comm
        rank = comm.rank

        sizes, offsets = evenly_distrib_idxs(comm.size, nn)  # (#cpus, #inputs) -> (size array, offset array)
        self.start_idx = offsets[rank]
        self.io_size = sizes[rank]  # number of inputs and outputs managed by this distributed process
        self.end_idx = self.start_idx + self.io_size

        # inputs: 2 states and a control
        #self.add_input('x0', val=np.ones(nn), desc='derivative of Output', units='V/s')
        #self.add_input('x1', val=np.ones(nn), desc='Output', units='V')
        #self.add_input('u', val=np.ones(nn), desc='control', units=None)
        self.add_input('x0', val=np.ones(nn), desc='derivative of Output', units=None)
        self.add_input('x1', val=np.ones(nn), desc='Output', units=None)
        self.add_input('u', val=np.ones(nn), desc='control', units=None)

        # outputs: derivative of states
        # the objective function will be treated as a state for computation, so its derivative is an output
        # self.add_output('x0dot', val=np.ones(self.io_size), desc='second derivative of Output',
        #                 units='V/s**2', distributed=self.options['distrib'])
        # self.add_output('x1dot', val=np.ones(self.io_size), desc='derivative of Output',
        #                 units='V/s', distributed=self.options['distrib'])
        # self.add_output('Jdot', val=np.ones(self.io_size), desc='derivative of objective',
        #                 units='1.0/s', distributed=self.options['distrib'])
        self.add_output('x0dot', val=np.ones(self.io_size), desc='second derivative of Output',
                units="1.0/s", distributed=self.options['distrib'])
        self.add_output('x1dot', val=np.ones(self.io_size), desc='derivative of Output',
                        units="1.0/s", distributed=self.options['distrib'])
        self.add_output('Jdot', val=np.ones(self.io_size), desc='derivative of objective',
                        units="1.0/s", distributed=self.options['distrib'])

        # self.declare_coloring(method='cs')
        # # partials
        r = np.arange(self.io_size, dtype=int)
        c = r + self.start_idx

        self.declare_partials(of='x0dot', wrt='x0',  rows=r, cols=c)
        self.declare_partials(of='x0dot', wrt='x1',  rows=r, cols=c)
        self.declare_partials(of='x0dot', wrt='u',   rows=r, cols=c, val=1.0)

        self.declare_partials(of='x1dot', wrt='x0',  rows=r, cols=c, val=1.0)

        self.declare_partials(of='Jdot', wrt='x0',  rows=r, cols=c)
        self.declare_partials(of='Jdot', wrt='x1',  rows=r, cols=c)
        self.declare_partials(of='Jdot', wrt='u',   rows=r, cols=c)

    def compute(self, inputs, outputs):

        # The inputs contain the entire vector, be each rank will only operate on a portion of it.
        x0 = inputs['x0'][self.start_idx:self.end_idx]
        x1 = inputs['x1'][self.start_idx:self.end_idx]
        u = inputs['u'][self.start_idx:self.end_idx]

        outputs['x0dot'] = (1.0 - x1**2) * x0 - x1 + u
        outputs['x1dot'] = x0
        outputs['Jdot'] = x0**2 + x1**2 + u**2

    def compute_partials(self, inputs, jacobian):
        x0 = inputs['x0'][self.start_idx:self.end_idx]
        x1 = inputs['x1'][self.start_idx:self.end_idx]
        u = inputs['u'][self.start_idx:self.end_idx]

        jacobian['x0dot', 'x0'] = 1.0 - x1 * x1
        jacobian['x0dot', 'x1'] = -2.0 * x1 * x0 - 1.0

        jacobian['Jdot', 'x0'] = 2.0 * x0
        jacobian['Jdot', 'x1'] = 2.0 * x1
        jacobian['Jdot', 'u'] = 2.0 * u
        
def vanderpol(transcription='gauss-lobatto', num_segments=15, transcription_order=3,
              compressed=True, optimizer='SLSQP', use_pyoptsparse=False):
    """Dymos problem definition for optimal control of a Van der Pol oscillator"""

    # define the OpenMDAO problem
    p = om.Problem(model=om.Group())

    if not use_pyoptsparse:
        p.driver = om.ScipyOptimizeDriver()
    else:
        p.driver = om.pyOptSparseDriver(print_results=False)
    p.driver.options['optimizer'] = optimizer
    if use_pyoptsparse:
        if optimizer == 'SNOPT':
            p.driver.opt_settings['iSumm'] = 6  # show detailed SNOPT output
        elif optimizer == 'IPOPT':
            p.driver.opt_settings['print_level'] = 4
    p.driver.declare_coloring()

    # define a Trajectory object and add to model
    traj = dm.Trajectory()
    p.model.add_subsystem('traj', subsys=traj)

    # define a Transcription
    if transcription == 'gauss-lobatto':
        t = dm.GaussLobatto(num_segments=num_segments,
                            order=transcription_order,
                            compressed=compressed)
    elif transcription == 'radau-ps':
        t = dm.Radau(num_segments=num_segments,
                     order=transcription_order,
                     compressed=compressed)

    # define a Phase as specified above and add to Phase
    phase = dm.Phase(ode_class=VanderpolODE, transcription=t)
    traj.add_phase(name='phase0', phase=phase)

    t_final = 10
    phase.set_time_options(fix_initial=True, fix_duration=True, duration_val=t_final, units='s')

    # set the State time options
    # phase.add_state('x0', fix_initial=True, fix_final=True,
    #                 rate_source='x0dot',
    #                 units='V/s', ref=0.1, defect_ref=0.1)  # target required because x0 is an input
    # phase.add_state('x1', fix_initial=True, fix_final=True,
    #                 rate_source='x1dot',
    #                 units='V', ref=0.1, defect_ref=0.1)
    # phase.add_state('J', fix_initial=True, fix_final=False,
    #                 rate_source='Jdot',
    #                 units=None)
    phase.add_state('x0', fix_initial=True, fix_final=True,
                    rate_source='x0dot',
                    units=None, ref=0.1, defect_ref=0.1)  # target required because x0 is an input
    phase.add_state('x1', fix_initial=True, fix_final=True,
                    rate_source='x1dot',
                    units=None, ref=0.1, defect_ref=0.1)
    phase.add_state('J', fix_initial=True, fix_final=False,
                    rate_source='Jdot',
                    units=None)

    # define the control
    phase.add_control(name='u', units=None, lower=-0.75, upper=1.0, continuity=True,
                      rate_continuity=True)

    # define objective to minimize
    phase.add_objective('J', loc='final')

    # setup the problem
    p.setup(check=True)

    p['traj.phase0.t_initial'] = 0.0
    p['traj.phase0.t_duration'] = t_final

    # add a linearly interpolated initial guess for the state and control curves
    p['traj.phase0.states:x0'] = phase.interp('x0', [0, 0])
    p['traj.phase0.states:x1'] = phase.interp('x1', [1, 0])
    p['traj.phase0.states:J'] = phase.interp('J', [0, 1])
    p['traj.phase0.controls:u'] = phase.interp('u', [0, 0])

    return p
    
if __name__ == "__main__":
    # Create the Dymos problem instance
    p = vanderpol(transcription='gauss-lobatto', num_segments=15,
                  transcription_order=3, compressed=True, optimizer='SLSQP')
    
    # Enable grid refinement and find optimal control solution to stop oscillation
    p.model.traj.phases.phase0.set_refine_options(refine=True)
    
    dm.run_problem(p, simulate=True, refine_iteration_limit=5, refine_method='hp')