import numpy as np
import openmdao.api as om
from PlanarQuadrotorODE import PlanarQuadrotorODE

num_nodes = 20

p = om.Problem(model=om.Group())

ivc = p.model.add_subsystem('vars', om.IndepVarComp())
ivc.add_output('u_1', shape=(num_nodes,), units='N')
ivc.add_output('u_2', shape=(num_nodes,), units='N')

p.model.add_subsystem('ode', PlanarQuadrotorODE(num_nodes=num_nodes))

p.model.connect('vars.u_1', 'ode.u_1')
p.model.connect('vars.u_2', 'ode.u_2')

p.setup(force_alloc_complex=True)

p.set_val('vars.u_1', 10*np.random.random(num_nodes))
p.set_val('vars.u_2', 10*np.random.random(num_nodes))

p.run_model()
cpd = p.check_partials(method='cs', compact_print=True)

# The Partials pass the test!