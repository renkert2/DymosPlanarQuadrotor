import numpy as np
import openmdao.api as om

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

class PlanarQuadrotorODE(om.ExplicitComponent):
    """
    Dymos ODE for Planar Quadrotor
    """

    def initialize(self):
        self.options.declare('num_nodes', types=int)

    def setup(self):
        nn = self.options['num_nodes']

        # Static Parameters
        self.add_input('g', val=9.80665, desc='grav. acceleration', units='m/s**2', tags=['dymos.static_target'])
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
        self.declare_partials(of='v_y_dot', wrt='g', val=-np.ones((self.options['num_nodes'], 1))) # Constant partial derivative -> value option is specified, no need to compute the partial

        self.declare_partials(of='omega_dot', wrt='u_1', rows=arange, cols=arange)
        self.declare_partials(of='omega_dot', wrt='u_2', rows=arange, cols=arange)
        self.declare_partials(of='omega_dot', wrt='r', rows=arange, cols=c)
        self.declare_partials(of='omega_dot', wrt='I', rows=arange, cols=c)

    def compute(self, inputs, outputs):
        g = inputs['g']
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