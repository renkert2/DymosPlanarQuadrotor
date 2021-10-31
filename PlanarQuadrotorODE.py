import numpy as np
import openmdao.api as om

class PlanarQuadrotorSizeComp(om.ExplicitComponent):
    def setup(self):
        self.add_input(name='rho', val=0.1, desc='frame density', units='kg/m')
        self.add_input(name='r', val=1, desc='arm length', units='m')

        self.add_output(name='m', shape=(1,), desc='quadrotor mass', units='kg')
        self.add_output(name='I', shape=(1,), desc='inertia', units='kg*m**2')
        self.add_output(name='r_out', val=1, desc='arm length', units='m')

        self.declare_partials(of='*', wrt='*', method='fd') # Would eventually want to include analytical derivatives
    def compute(self, inputs, outputs):
        r = inputs["r"]
        rho = inputs["rho"]

        m = rho*2*r
        outputs["m"] = m
        outputs["I"] = (1/12)*m*(2*r)**2
        outputs["r_out"] = r

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
        self.add_input('theta', shape=(nn,1), desc='attitude', units='rad')
        #self.add_input('omega', shape=(nn,1), desc='angular velocity', units='rad/s')
        self.add_input('u_1', shape=(nn,1), desc='thrust_input_1', units='N')
        self.add_input('u_2', shape=(nn,1), desc='thrust_input_2', units='N')

        # Outputs
        self.add_output('v_x_dot', shape=(nn,1), desc='rate of change velocity x', units='m/s**2')
        self.add_output('v_y_dot', shape=(nn,1), desc='rate of change velocity y', units='m/s**2')
        self.add_output('omega_dot', shape=(nn,1),desc='rate of change omega', units='rad/s**2')

        self.declare_partials(of='*', wrt='*', method='fd') # Would eventually want to include analytical derivatives
    
    def compute(self, inputs, outputs):
        g = inputs['g']
        m = inputs['m']
        r = inputs['r']
        I = inputs['I']
        theta = inputs['theta']
        u_1 = inputs['u_1']
        u_2 = inputs['u_2']

        outputs['v_x_dot']=-(1/m)*(u_1 + u_2)*np.sin(theta)
        outputs['v_y_dot']=-g + (1/m)*(u_1 + u_2)*np.cos(theta)
        outputs['omega_dot'] = r/I*(u_1 - u_2)

