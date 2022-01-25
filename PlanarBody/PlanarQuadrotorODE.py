import numpy as np
import openmdao.api as om

# CONSTANTS
g = 9.80665

class PlanarQuadrotorSizeComp(om.ExplicitComponent):
    def setup(self):
        self.add_input(name='rho', val=0.1, desc='frame density', units='kg/m')
        self.add_input(name='r', val=1, desc='arm length', units='m')

        self.add_output(name='m', shape=(1,), desc='quadrotor mass', units='kg')
        self.add_output(name='I', shape=(1,), desc='inertia', units='kg*m**2')

        #self.declare_partials(of='*', wrt='*', method='fd') # Would eventually want to include analytical derivatives
        self.declare_partials(of='m', wrt='rho')
        self.declare_partials(of='m', wrt='r')
        
        self.declare_partials(of='I', wrt='rho')
        self.declare_partials(of='I', wrt='r')
    
    def compute(self, inputs, outputs):
        r = inputs["r"]
        rho = inputs["rho"]

        m = rho*2*r
        outputs["m"] = m
        outputs["I"] = (1/12)*m*(2*r)**2

    def compute_partials(self, inputs, partials):
        r = inputs["r"]
        rho = inputs["rho"]

        partials["m", "rho"] = 2*r
        partials["m", "r"] = 2*rho

        partials["I", "rho"] = (2*r**3)/3
        partials["I", "r"] = (2*r**2)*rho

class PlanarQuadrotorHover(om.ExplicitComponent):
    """
    Used to Calculate the Steady-State Thrust requried for Hover
    """
    
    def setup(self):

        # Static Parameters
        self.add_input('m', val=1, desc='mass', units='kg')
        
        # Outputs
        self.add_output("u_hover", desc="Hover Thrust Input", units="N")
        
    def setup_partials(self):
        self.declare_partials(of="u_hover", wrt="m", val=g)

    def compute(self, inputs, outputs):
        m = inputs['m']

        outputs['u_hover'] = m*g
        
class PlanarQuadrotorVertAccel(om.ExplicitComponent):
    """
    Used to Calculate the Steady-State Thrust requried for Hover
    """
    
    def setup(self):

        # Static Parameters
        self.add_input('m', val=1, desc='mass', units='kg')
        
        # Inputs
        self.add_input("u", desc="Thrust Input", units="N")
        
        # Outputs
        self.add_output("a", desc="Vertical Acceleration", units="m/s**2")
    
    def setup_partials(self):
        self.declare_partials(of="a", wrt="m")
        self.declare_partials(of="a", wrt="u")

    def compute(self, inputs, outputs):
        m = inputs['m']
        u = inputs["u"]

        outputs['a'] = u/m - g
        
    def compute_partials(self, inputs, partials):
        m = inputs['m']
        u = inputs["u"]
        
        partials["a", "m"] = -(1/(m**2)) * u
        partials["a", "u"] = 1/m

class PlanarQuadrotorODE(om.ExplicitComponent):
    """
    Dymos ODE for Planar Quadrotor
    """

    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']

        # Static Parameters
        self.add_input('m', val=1, desc='mass', units='kg', tags=['dymos.static_target'])
        self.add_input('r', val=0.1, desc='arm length', units='m', tags=['dymos.static_target'])
        self.add_input('I', val=0.01, desc='inertia', units='kg*m**2', tags=['dymos.static_target'])
        

        # Dynamic Variables Inputs
        #self.add_input('x', shape=(nn,2), desc='position', units='m')
        #self.add_input('v', shape=(nn,2), desc='velocity', units='m/s')
        self.add_input('theta', shape=(nn,), desc='attitude', units='rad')
        #self.add_input('omega', shape=(nn,1), desc='angular velocity', units='rad/s')
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
        self.declare_partials(of='v_x_dot', wrt='m', rows=arange, cols=c)

        self.declare_partials(of='v_y_dot', wrt='u_1', rows=arange, cols=arange)
        self.declare_partials(of='v_y_dot', wrt='u_2', rows=arange, cols=arange)
        self.declare_partials(of='v_y_dot', wrt='theta', rows=arange, cols=arange)
        self.declare_partials(of='v_y_dot', wrt='m', rows=arange, cols=c)

        self.declare_partials(of='omega_dot', wrt='u_1', rows=arange, cols=arange)
        self.declare_partials(of='omega_dot', wrt='u_2', rows=arange, cols=arange)
        self.declare_partials(of='omega_dot', wrt='r', rows=arange, cols=c)
        self.declare_partials(of='omega_dot', wrt='I', rows=arange, cols=c)

    def compute(self, inputs, outputs):
        m = inputs['m']
        r = inputs['r']
        I = inputs['I']
        theta = inputs['theta']
        u_1 = inputs['u_1']
        u_2 = inputs['u_2']

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        outputs['v_x_dot']=-(1/m)*(u_1 + u_2)*sin_theta
        outputs['v_y_dot']=-g + (1/m)*(u_1 + u_2)*cos_theta
        outputs['omega_dot'] = r/I*(u_1 - u_2)

    def compute_partials(self, inputs, partials):
        m = inputs['m']
        r = inputs['r']
        I = inputs['I']
        theta = inputs['theta']
        u_1 = inputs['u_1']
        u_2 = inputs['u_2']

        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)

        partials['v_x_dot', 'u_1'] = -sin_theta/m
        partials['v_x_dot', 'u_2'] = -sin_theta/m
        partials['v_x_dot', 'theta'] = -(1/m)*cos_theta*(u_1 + u_2)
        partials['v_x_dot', 'm'] = (1/m**2)*sin_theta*(u_1 + u_2)

        partials['v_y_dot', 'u_1'] = cos_theta/m
        partials['v_y_dot', 'u_2'] = cos_theta/m
        partials['v_y_dot', 'theta'] = -(1/m)*sin_theta*(u_1 + u_2)
        partials['v_y_dot', 'm'] = -(1/m**2)*cos_theta*(u_1 + u_2)

        partials['omega_dot', 'u_1'] = r/I
        partials['omega_dot', 'u_2'] = -r/I
        partials['omega_dot', 'r'] = (u_1 - u_2)/I
        partials['omega_dot', 'I'] = -(r/(I**2))*(u_1 - u_2)
        
def ModifyPhase(phase, openmdao_path="", declare_controls=True):
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
    
    # Define constant parameters
    phase.add_parameter(V2N('g'), units='m/s**2', val=9.80665)
    phase.add_parameter(V2N('m'), units='kg', val=1)
    phase.add_parameter(V2N('r'), units='m', val=.1)
    phase.add_parameter(V2N('I'), units='kg*m**2', val=1)
    
    return phase