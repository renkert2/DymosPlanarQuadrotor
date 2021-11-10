import openmdao.api as om
import dymos as dm
import matplotlib.pyplot as plt
from PlanarQuadrotorODE import PlanarQuadrotorODE, PlanarQuadrotorSizeComp


def main():
    p, phase, traj = init()

    #
    # Setup the problem
    #
    p, phase = setup(p,phase)
    attach_recorder(p, 'without_plant_vars.sql')
    initial_des_vars = [p.get_val('rho'), p.get_val('r')]

    #
    # Run the Optimization Problem - No Plant Optimization
    #
    print("Optimizing without Plant Design Variables")
    run_problem(p)
    p.record('final')
    initial_tf = p.get_val('traj.phase0.timeseries.time')[-1]
    p_initial = get_data(p)
    exp_out = traj.simulate()  # Forward Simulate the trajectory with the optimized results
    p.cleanup()
    initial_des_vars_1 = [p.get_val('rho'), p.get_val('r')]

    #
    # Setup the problem with Plant Optimization
    #
    p.model.add_design_var('rho', lower=0.5, upper=1, units='kg/m')
    p.model.add_design_var('r', lower=0.1, upper=1, units='m')
    p, phase = setup(p,phase)
    attach_recorder(p, 'with_plant_vars.sql')

    #
    # Run the Optimization Problem - Plant Optimization
    #
    print("Optimizing With Plant Design Variables")
    run_problem(p)
    p.record("final")
    final_tf = p.get_val('traj.phase0.timeseries.time')[-1]
    p_final = get_data(p)
    # Forward Simulate the trajectory with the optimized results
    exp_out_plant = traj.simulate()
    p.cleanup()
    final_des_vars = [p.get_val('rho'), p.get_val('r')]

    sim_plots([('traj.phase0.timeseries.time', 'traj.phase0.timeseries.states:x',
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
                'Minimum Time Solution\nRadau Psuedospectral Method',
                [exp_out, exp_out_plant],
                [p_initial, p_final],
                legenddesc=["Initial Plant", "Optimal Plant"])

    plt.show()

    print("Initial Des Vars:")
    print(initial_des_vars)
    print(initial_des_vars_1)

    print("Final Des Vars:")
    print(final_des_vars)

    print("Initial Time")
    print(initial_tf)

    print("Final Time")
    print(final_tf)

def init():
    #
    # Initialize Problem and Optimization Driver
    #
    p = om.Problem(model=om.Group())
    p.driver = om.ScipyOptimizeDriver()
    p.driver.options['optimizer'] = 'SLSQP'
    p.driver.options['disp'] = True
    p.driver.options['maxiter'] = 1000

    p.driver.declare_coloring()
    # p.driver.options['debug_print'] = ['desvars','ln_cons','nl_cons','objs']
    # p.set_solver_print(level=0)

    # Add Sizing Subsystem
    p.model.add_subsystem('size_comp', PlanarQuadrotorSizeComp(),
                      promotes_inputs=['rho', 'r'])
    p.model.set_input_defaults('rho', val=0.1, units='kg/m')
    p.model.set_input_defaults('r', val=1, units='m')

    #
    # Create a trajectory and add a phase to it
    #
    transcription_segments = 10
    #trans = dm.GaussLobatto(num_segments=transcription_segments, compressed=True)
    trans = dm.Radau(num_segments=transcription_segments, compressed=True)
    traj = p.model.add_subsystem('traj', dm.Trajectory())
    phase = traj.add_phase('phase0', dm.Phase(ode_class=PlanarQuadrotorODE,
                        transcription=trans))

    #
    # Set the Variables
    #
    phase.set_time_options(fix_initial=True, duration_bounds=(0.01, 100))

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
    phase.add_parameter('g', units='m/s**2', static_target=True, val=9.80665)
    phase.add_parameter('m', units='kg', static_target=True)
    phase.add_parameter('r', units='m', static_target=True)
    phase.add_parameter('I', units='kg*m**2')

    # Add Final Derivative Constraints to enforce that the inputs at the final time are at their steady-state values
    phase.add_boundary_constraint('v_y_dot', loc='final', shape=(1,), equals=0, units='m/s**2')
    phase.add_boundary_constraint('omega_dot', loc='final', shape=(1,), equals=0, units='rad/s**2')

    # Make Parameter Connections
    p.model.promotes('traj', inputs=[('phase0.parameters:r','r')])
    p.model.connect('size_comp.m', 'traj.phase0.parameters:m')
    p.model.connect('size_comp.I', 'traj.phase0.parameters:I')

    #
    # Minimize time at the end of the phase
    #
    phase.add_objective('time', loc='final')
    p.model.linear_solver = om.DirectSolver()

    return p, phase, traj

def setup(p,phase):
    p.setup(check=True)

    #
    # Set the Initial Values
    #
    p.set_val('rho', val=1, units='kg/m')
    p.set_val('r', val=1, units='m')

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

    return p, phase

def run_problem(problem):
    problem.final_setup()
    failed = problem.run_driver()
    return failed

def attach_recorder(p, case_recorder_filename):
    recorder = om.SqliteRecorder(case_recorder_filename)
    # Attach a recorder to the problem
    p.add_recorder(recorder)
    p.recording_options['record_desvars'] = True
    p.recording_options['record_responses'] = True
    p.recording_options['record_objectives'] = True
    p.recording_options['record_constraints'] = True
    p.recording_options['record_inputs'] = True
    p.recording_options['includes'] = ['*timeseries*']
    
    p.driver.add_recorder(recorder)
    
    

def get_data(problem):
    names = ['traj.phase0.timeseries.time',
                'traj.phase0.timeseries.states:x',
                'traj.phase0.timeseries.states:y',
                'traj.phase0.timeseries.states:theta',
                'traj.phase0.timeseries.controls:u_1',
                'traj.phase0.timeseries.controls:u_2',
                ]
    prob_dat = {}
    for name in names:
        prob_dat[name]=problem.get_val(name)
    
    return prob_dat
    
def sim_plots(axes, title, sim_array, sol_array, figsize=(10, 8), legenddesc=None):
    nrows = len(axes)

    fig, axs = plt.subplots(nrows=nrows, ncols=1, figsize=figsize)
    fig.suptitle(title)

    if nrows == 1:
        axs = [axs]

    for i, (x, y, xlabel, ylabel) in enumerate(axes):
        for j, p_sim in enumerate(sim_array):
            p_sol = sol_array[j]
            axs[i].plot(p_sim[x],
                        p_sim[y],
                        marker=None,
                        linestyle='-',
                        label=legenddesc[j] if i == 0 else None)
            axs[i].plot(p_sol[x],
                        p_sol[y],
                        marker='o',
                        ms=4,
                        linestyle='None')

            axs[i].set_xlabel(xlabel)
            axs[i].set_ylabel(ylabel)
            fig.suptitle(title)
            fig.legend(loc='lower center', ncol=2)

    return fig, axs
if __name__ == "__main__":
    main()
