#%%
import openmdao.api as om
import os
import sys
os.chdir(os.path.join(os.path.dirname(__file__), "..")) # Go up to Level containing Models
import SharedFunctions as sf
import DynamicModel as dm
import dymos
import logging
import numpy as np
import matplotlib.pyplot as plt
mtlb = os.getenv('MYPYTHON')
plt.style.use(os.path.join(mtlb, 'research_default.mplstyle'))

logging.basicConfig(level=logging.DEBUG)

#%%
mdl = "PlanarPowerTrainModel_Simple"
path = "."

#Functions: h, f, g
tx = dymos.GaussLobatto(num_segments=10, solve_segments='forward')
phase = dm.DynamicPhase(ode_class=dm.DynamicModel, model=mdl, path=path, model_kwargs={"Functions":["h", "f", "g"]}, transcription=tx)

phase.init_vars(openmdao_path='', 
                    state_names = ["x"], control_names = ["u", "d"], parameter_names = ["theta"], output_names = ["y", "a"],
                    var_opts = {"x":{},"u":{},"d":{},"theta":{}}
                  )
phase.name = "phase0"
phase.add_objective('time', loc='final')
phase.set_time_options(fix_initial=True, initial_val=0, fix_duration=True, duration_val=10)
phase.set_control_options('u1', val=1, fix_initial=True, fix_final=True)
phase.set_state_options('x1', val=0, fix_initial=True)

prob = om.Problem(model=om.Group())
prob.driver = om.ScipyOptimizeDriver()
traj = dymos.Trajectory()
traj.add_phase('phase0', phase)

prob.model.add_subsystem('traj', traj)
prob.model.linear_solver = om.DirectSolver() # I'm not sure why we need this

prob.setup(force_alloc_complex=True)
prob.final_setup()

prob.set_val('traj.phase0.states:x1', 0)
prob.set_val('traj.phase0.controls:u1', 1)
prob.run_model()

inputs = ['states:x1', 'controls:u1', 'outputs:y1', 'outputs:a2']
labels = ["Rotor Speed", "Inverter Input", "Output Thrust", "Bus Current"]
t = prob.get_val('traj.phase0.timeseries.time')
fig, axes = plt.subplots(len(inputs), 1)
for i, input in enumerate(inputs):
    sol = axes[i].plot(t, prob.get_val(f'traj.phase0.timeseries.{input}'), '-')
    axes[i].set_ylabel(labels[i])
axes[-1].set_xlabel('time (s)')
plt.tight_layout()
plt.savefig('FowardSimulation.png')
plt.show()
#%%



