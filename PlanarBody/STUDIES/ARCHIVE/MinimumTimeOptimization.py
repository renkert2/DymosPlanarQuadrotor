import openmdao.api as om
import dymos as dm
from dymos.examples.plotting import plot_results
import matplotlib.pyplot as plt

from PlanarQuadrotorODE import PlanarQuadrotorODE

#
# Initialize Problem and Optimization Driver
#
p = om.Problem(model=om.Group())
p.driver = om.ScipyOptimizeDriver()
p.driver.declare_coloring()

#
# Create a trajectory and add a phase to it
#
transcription_segments = 10
traj = p.model.add_subsystem('traj', dm.Trajectory())
trans = dm.GaussLobatto(num_segments=transcription_segments) # Number of nodes required for downstream calculations
phase = traj.add_phase('phase0', dm.Phase(ode_class=PlanarQuadrotorODE,
                       transcription=trans))

#
# Set the Variables
#
phase.set_time_options(fix_initial=True, duration_bounds=(0.5, 100))

# Tell Dymos the states to be propagated using the given ODE.
phase.add_state('v_x', fix_initial=True, fix_final=True,
                rate_source='v_x_dot', units='m/s')
phase.add_state('v_y', fix_initial=True, fix_final=True,
                rate_source='v_y_dot', units='m/s')

phase.add_state('x', fix_initial=True, fix_final=True,
                rate_source='v_x', units='m')
phase.add_state('y', fix_initial=True, fix_final=True,
                rate_source='v_y', units='m')

phase.add_state('omega', fix_initial=True, fix_final=True,
                rate_source='omega_dot', units='rad/s')
phase.add_state('theta', fix_initial=True, fix_final=True,
                rate_source='omega', targets=['theta'], units='rad')

# Add Inputs
phase.add_control('u_1', continuity=True, rate_continuity=True,
                  lower=0, upper=20, targets=['u_1'], units='N')
phase.add_control('u_2', continuity=True, rate_continuity=True,
                  lower=0, upper=20, targets=['u_2'], units='N')

# Define constant parameters
phase.add_parameter('g', units='m/s**2', val=9.80665)
phase.add_parameter('m', units='kg', val=1)
phase.add_parameter('r', units='m', val=.1)
phase.add_parameter('I', units='kg*m**2', val=1)

# Add Final Derivative Constraints to enforce that the inputs at the final time are at their steady-state values

phase.add_boundary_constraint('v_y_dot', loc='final', shape=(1,), equals=0, units='m/s**2')
phase.add_boundary_constraint('omega_dot', loc='final', shape=(1,), equals=0, units='rad/s**2')

#
# Minimize time at the end of the phase
#
phase.add_objective('time', loc='final')
p.model.linear_solver = om.DirectSolver()

#
# Setup the problem
#
p.setup()

#
# Set the Initial Values
#
p.set_val('traj.phase0.t_initial', 0.0)
p.set_val('traj.phase0.t_duration', 100.0)

p.set_val('traj.phase0.states:v_x', phase.interp('v_x', ys=[0, 0]))
p.set_val('traj.phase0.states:v_y', phase.interp('v_y', ys=[0, 0]))
p.set_val('traj.phase0.states:x', phase.interp('x', ys=[0, 10]))
p.set_val('traj.phase0.states:y', phase.interp('y', ys=[0, 10]))
p.set_val('traj.phase0.states:omega', phase.interp('omega', ys=[0, 0]))
p.set_val('traj.phase0.states:theta', phase.interp('theta', ys=[0, 0]))

p.set_val('traj.phase0.controls:u_1', phase.interp('u_1', ys=[10, 10]))
p.set_val('traj.phase0.controls:u_2', phase.interp('u_2', ys=[10, 10]))

#
# Run the Optimization Problem
#
dm.run_problem(p)

#
# Analyze Results
#
print(p.get_val('traj.phase0.timeseries.time')[-1])

# Forward Simulate the trajectory with the optimized results
exp_out = traj.simulate()

plot_results([('traj.phase0.timeseries.time', 'traj.phase0.timeseries.states:x',
               't (s)', 'x (m)'),
              ('traj.phase0.timeseries.time', 'traj.phase0.timeseries.states:y',
               't (s)', 'y (m)'),
              ('traj.phase0.timeseries.time', 'traj.phase0.timeseries.states:theta',
               'time (s)', 'theta (rad)'),
              ('traj.phase0.timeseries.time', 'traj.phase0.timeseries.controls:u_1',
             'time (s)', 'u_1 (N)'),
              ('traj.phase0.timeseries.time', 'traj.phase0.timeseries.controls:u_2',
               'time (s)', 'u_2 (N)'),
              ],
             title='Minimum Time Solution\nHigh-Order Gauss-Lobatto Method',
             p_sol=p, p_sim=exp_out)

plt.show()
