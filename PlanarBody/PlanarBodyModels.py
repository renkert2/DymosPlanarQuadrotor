import numpy as np
import openmdao.api as om
import os
import GraphTools_Phil_V2.OpenMDAO.DynamicModel as DM

g = 9.80665
       
class PlanarBodyODE(om.ExplicitComponent):
    """
    Dymos ODE for Planar Quadrotor
    """

    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']

        # Static Parameters
        self.add_input('Mass__System', shape = (1,), val=1, desc='mass', units='kg', tags=['dymos.static_target'])
        self.add_input('r__Frame', shape = (1,), val=0.1, desc='arm length', units='m', tags=['dymos.static_target'])
        self.add_input('I__System', shape = (1,), val=0.01, desc='inertia', units='kg*m**2', tags=['dymos.static_target'])
        

        # Dynamic Variables Inputs
        self.add_input('theta', shape=(nn,), desc='attitude', units='rad')
        self.add_input('u_1', shape=(nn,), desc='thrust_input_1', units='N')
        self.add_input('u_2', shape=(nn,), desc='thrust_input_2', units='N')

        # Outputs
        self.add_output('v_x_dot', shape=(nn,), desc='rate of change velocity x', units='m/s**2')
        self.add_output('v_y_dot', shape=(nn,), desc='rate of change velocity y', units='m/s**2')
        self.add_output('omega_dot', shape=(nn,),desc='rate of change omega', units='rad/s**2')

        # self.declare_partials(of='*', wrt='*', method='fd') # Would eventually want to include analytical derivatives
        arange = np.arange(self.options['num_nodes'])
        c = np.zeros(self.options['num_nodes'])
        
        # See Sparse Partial Derivatives documentation: https://openmdao.org/newdocs/versions/latest/features/core_features/working_with_derivatives/sparse_partials.html
        self.declare_partials(of='v_x_dot', wrt='u_1', rows=arange, cols=arange)
        self.declare_partials(of='v_x_dot', wrt='u_2', rows=arange, cols=arange)
        self.declare_partials(of='v_x_dot', wrt='theta', rows=arange, cols=arange)
        self.declare_partials(of='v_x_dot', wrt='Mass__System', rows=arange, cols=c)

        self.declare_partials(of='v_y_dot', wrt='u_1', rows=arange, cols=arange)
        self.declare_partials(of='v_y_dot', wrt='u_2', rows=arange, cols=arange)
        self.declare_partials(of='v_y_dot', wrt='theta', rows=arange, cols=arange)
        self.declare_partials(of='v_y_dot', wrt='Mass__System', rows=arange, cols=c)

        self.declare_partials(of='omega_dot', wrt='u_1', rows=arange, cols=arange)
        self.declare_partials(of='omega_dot', wrt='u_2', rows=arange, cols=arange)
        self.declare_partials(of='omega_dot', wrt='r__Frame', rows=arange, cols=c)
        self.declare_partials(of='omega_dot', wrt='I__System', rows=arange, cols=c)

    def compute(self, inputs, outputs):
        m = inputs['Mass__System']
        r = inputs['r__Frame']
        I = inputs['I__System']
        theta = inputs['theta']
        u_1 = inputs['u_1']
        u_2 = inputs['u_2']

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        outputs['v_x_dot']=-(1/m)*(u_1 + u_2)*sin_theta
        outputs['v_y_dot']=-g + (1/m)*(u_1 + u_2)*cos_theta
        outputs['omega_dot'] = r/I*(u_1 - u_2)
        pass

    def compute_partials(self, inputs, partials):
        m = inputs['Mass__System']
        r = inputs['r__Frame']
        I = inputs['I__System']
        theta = inputs['theta']
        u_1 = inputs['u_1']
        u_2 = inputs['u_2']

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        partials['v_x_dot', 'u_1'] = -sin_theta/m
        partials['v_x_dot', 'u_2'] = -sin_theta/m
        partials['v_x_dot', 'theta'] = -(1/m)*cos_theta*(u_1 + u_2)
        partials['v_x_dot', 'Mass__System'] = (1/m**2)*sin_theta*(u_1 + u_2)

        partials['v_y_dot', 'u_1'] = cos_theta/m
        partials['v_y_dot', 'u_2'] = cos_theta/m
        partials['v_y_dot', 'theta'] = -(1/m)*sin_theta*(u_1 + u_2)
        partials['v_y_dot', 'Mass__System'] = -(1/m**2)*cos_theta*(u_1 + u_2)

        partials['omega_dot', 'u_1'] = r/I
        partials['omega_dot', 'u_2'] = -r/I
        partials['omega_dot', 'r__Frame'] = (u_1 - u_2)/I
        partials['omega_dot', 'I__System'] = -(r/(I**2))*(u_1 - u_2)
        
def genRenameFunctions(openmdao_path):
    def V2T(var):
        # If path to OpenMDAO Variable is specified, Convert it to target openmdao path
        if openmdao_path:
            target = openmdao_path + "." + var
        else:
            target = var
        return target
    
    def V2N(var):
        # If path to OpenMDAO Variable is specified, prepend it to the variable name
        if openmdao_path:
            name = openmdao_path + "_" + var
        else:
            name = var
        return name
    
    return(V2T, V2N)
        
def ModifyPhase(phase, openmdao_path="", declare_controls=True):
    (V2T, V2N) = genRenameFunctions(openmdao_path)

    phase.add_state(V2N('v_x'), rate_source=V2T('v_x_dot'), units='m/s')
    phase.add_state(V2N('v_y'), rate_source=V2T('v_y_dot'), units='m/s')
    
    phase.add_state(V2N('x'), rate_source=V2N('v_x'), units='m')
    phase.add_state(V2N('y'), rate_source=V2N('v_y'), units='m')
    
    phase.add_state(V2N('omega'), rate_source=V2T('omega_dot'), units='rad/s')
    phase.add_state(V2N('theta'), rate_source=V2N('omega'), targets=[V2T('theta')], units='rad')
    
    # Add Inputs
    if declare_controls:
        phase.add_control(V2N('u_1'), targets=[V2T('u_1')], units='N')
        phase.add_control(V2N('u_2'), targets=[V2T('u_2')], units='N')

    
    return phase

def ModifyTraj(traj, openmdao_path=""):
    # Define constant parameters
    (V2T, V2N) = genRenameFunctions(openmdao_path)
    
    phase_names = traj._phases.keys()
    
    # We want the parameter names to remain without unchanged regardless of the path so that the ParamSystem can find them. 
    opts = {'opt':False,'static_target':True}

    traj.add_parameter("Mass__System", targets={p:[V2T('Mass__System')] for p in phase_names}, **opts)
    traj.add_parameter("r__Frame", targets={p:[V2T('r__Frame')] for p in phase_names}, **opts)
    traj.add_parameter("I__System", targets={p:[V2T('I__System')] for p in phase_names}, **opts)
    
if __name__ == "__main__":
    # Run N2 and Model Checks
    import openmdao.api as om
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    os.chdir(os.path.dirname(__file__))
    try:
        os.mkdir('./ModelChecks/')
    except:
        pass
    os.chdir('./ModelChecks/')
    
    def checkModelClass(model_class):
        class_name = model_class.__name__
        
        if not os.path.isdir(class_name):
            os.mkdir(class_name)
        os.chdir(class_name)
        
        print(f"Checking Model Class: {class_name}")
        
        mdl_args = {"num_nodes":10}
        p = om.Problem(model=om.Group())
        p.model.add_subsystem("sys", model_class(**mdl_args))
        p.setup()
        p.final_setup()
        
        # Visualize:
        om.n2(p)
        #om.view_connections(p)
        
        # Checks:
        p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
        p.check_partials(compact_print=True)
        
        os.chdir('..')
    
    #model_types = [PlanarPTModelDAE, PlanarPTModelDAE_Simple]
    model_types = [PlanarBodyODE]
    
    for mtype in model_types:
        checkModelClass(mtype)