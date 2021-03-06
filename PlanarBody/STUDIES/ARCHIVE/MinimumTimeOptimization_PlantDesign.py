import openmdao.api as om
import dymos as dm
#from dymos.examples.plotting import plot_results
from dymos.examples.brachistochrone import BrachistochroneODE
import matplotlib.pyplot as plt
import copy
from PlanarQuadrotorODE import PlanarQuadrotorODE


def main():
    case_recorder_filename = 'cases.sql'
    p, phase, traj = init(case_recorder_filename)

    #
    # Setup the problem
    #
    p, phase = setup(p,phase)

    #
    # Run the Optimization Problem - No Plant Optimization
    #
    print("Optimizing without Plant Design Variables")
    run_problem(p)
    p.record("no_plant_vars")
    initial_tf = p.get_val('traj.phase0.timeseries.time')[-1]
    exp_out = traj.simulate()  # Forward Simulate the trajectory with the optimized results
    p.cleanup()

    #
    # Setup the problem with Plant Optimization
    #
    phase.set_parameter_options('m', opt=True, lower=0.1)
    phase.set_parameter_options('r', opt=True, lower=0.01)
    phase.set_parameter_options('I', opt=True, lower=0.01)
    p, phase = setup(p,phase)
    

    #
    # Run the Optimization Problem - Plant Optimization
    #
    print("Optimizing With Plant Design Variables")
    run_problem(p)
    final_tf = p.get_val('traj.phase0.timeseries.time')[-1]
    # Forward Simulate the trajectory with the optimized results
    exp_out_plant = traj.simulate()
    p.cleanup()

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
                'Minimum Time Solution\nHigh-Order Gauss-Lobatto Method',
                [exp_out, exp_out_plant],
                legenddesc=["Initial Plant", "Optimal Plant"])

    plt.show()

def init(case_recorder_filename):
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
    phase = traj.add_phase('phase0', dm.Phase(ode_class=PlanarQuadrotorODE,
                        transcription=dm.GaussLobatto(num_segments=transcription_segments)))

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
    phase.add_parameter('g', units='m/s**2', static_target=True, val=9.80665)
    phase.add_parameter('m', units='kg', static_target=True, val=2)
    phase.add_parameter('r', units='m', static_target=True, val=.1)
    phase.add_parameter('I', units='kg*m**2', val=1)

    #
    # Minimize time at the end of the phase
    #
    phase.add_objective('time', loc='final')
    p.model.linear_solver = om.DirectSolver()

    # Create a recorder variable and Case Reader Variable

    recorder = om.SqliteRecorder(case_recorder_filename)
    # Attach a recorder to the problem
    p.add_recorder(recorder)
    p.recording_options['record_desvars'] = True
    p.recording_options['record_responses'] = True
    p.recording_options['record_objectives'] = True
    p.recording_options['record_constraints'] = True
    p.recording_options['record_inputs'] = True
    p.recording_options['includes'] = ['*timeseries*']

    return p, phase, traj

def setup(p,phase):
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

    return p, phase

def run_problem(problem):
    problem.final_setup()
    failed = problem.run_driver()

    return failed

def sim_plots(axes, title, sim_array, figsize=(10, 8), legenddesc=None):
    nrows = len(axes)

    fig, axs = plt.subplots(nrows=nrows, ncols=1, figsize=figsize)
    fig.suptitle(title)

    if nrows == 1:
        axs = [axs]

    for i, (x, y, xlabel, ylabel) in enumerate(axes):
        for j, p_sim in enumerate(sim_array):
            axs[i].plot(p_sim.get_val(x),
                        p_sim.get_val(y),
                        marker=None,
                        linestyle='-',
                        label=legenddesc[j] if i == 0 else None)

            axs[i].set_xlabel(xlabel)
            axs[i].set_ylabel(ylabel)
            fig.suptitle(title)
            fig.legend(loc='lower center', ncol=2)

    return fig, axs
if __name__ == "__main__":
    main()
