### SOURCE: https://openmdao.github.io/dymos/getting_started/intro_to_dymos/intro_ivp.html
# %%
import openmdao.api as om
import dymos as dm
import matplotlib.pyplot as plt

from PlanarQuadrotorODE import PlanarQuadrotorODE

prob = om.Problem()

# Instantiate a Dymos Trajectory and add it to the Problem model
traj = dm.Trajectory()
prob.model.add_subsystem('traj', traj)

# Instantiate a Phase and add it to the Trajectory.
# Here the transcription is necessary but not particularly relevant.
phase = dm.Phase(ode_class=PlanarQuadrotorODE, transcription=dm.Radau(num_segments=4))
traj.add_phase('phase0', phase)

# Tell Dymos the states to be propagated using the given ODE.
phase.add_state('v_x', rate_source='v_x_dot', units='m/s')
phase.add_state('v_y', rate_source='v_y_dot', units='m/s')

phase.add_state('x', rate_source='v_x', units='m')
phase.add_state('y', rate_source='v_y', units='m')

phase.add_state('omega', rate_source='omega_dot', units='rad/s')
phase.add_state('theta', rate_source='omega', targets=['theta'], units='rad')

# Add Inputs
phase.add_control('u_1', targets=['u_1'], units='N')
phase.add_control('u_2', targets=['u_2'], units='N')

# Define constant parameters
phase.add_parameter('g', units='m/s**2', val=9.80665)
phase.add_parameter('m', units='kg', val=1)
phase.add_parameter('r', units='m', val=.1)
phase.add_parameter('I', units='kg*m**2', val=1)

prob.setup()
prob.set_val('traj.phase0.t_initial', 0.0)
prob.set_val('traj.phase0.t_duration', 2.0)

prob.set_val('traj.phase0.states:v_x', 0)
prob.set_val('traj.phase0.states:v_y', 0)
prob.set_val('traj.phase0.states:x', 0)
prob.set_val('traj.phase0.states:y', 0)
prob.set_val('traj.phase0.states:omega', 0)
prob.set_val('traj.phase0.states:theta', 0)

prob.set_val('traj.phase0.controls:u_1', 0)
prob.set_val('traj.phase0.controls:u_2', 20)
# %%
prob.run_model()

sim_out = traj.simulate(times_per_seg=50)

t_sol = prob.get_val('traj.phase0.timeseries.time')
t_sim = sim_out.get_val('traj.phase0.timeseries.time')

states = ['x', 'y', 'theta']
fig, axes = plt.subplots(len(states), 1)
for i, state in enumerate(states):
    # sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.states:{state}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.states:{state}'), '-')
    axes[i].set_ylabel(state)
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

inputs = ['u_1', 'u_2']
fig, axes = plt.subplots(len(inputs), 1)
for i, input in enumerate(inputs):
    # sol = axes[i].plot(t_sol, prob.get_val(f'traj.phase0.timeseries.controls:{input}'), 'o')
    sim = axes[i].plot(t_sim, sim_out.get_val(f'traj.phase0.timeseries.controls:{input}'), '-')
    axes[i].set_ylabel(input)
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.show()

# %%
