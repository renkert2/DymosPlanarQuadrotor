import openmdao.api as om
from openmdao.test_suite.components.sellar import SellarDerivatives

import numpy as np

prob = om.Problem(model=SellarDerivatives())

model = prob.model
model.add_design_var('z', lower=np.array([-10.0, 0.0]),
                          upper=np.array([10.0, 10.0]))
model.add_design_var('x', lower=0.0, upper=10.0)
model.add_objective('obj')
model.add_constraint('con1', upper=0.0)
model.add_constraint('con2', upper=0.0)

prob.driver = om.ScipyOptimizeDriver(optimizer='SLSQP', tol=1e-9)

prob.add_recorder(om.SqliteRecorder("cases_ex.sql"))

prob.recording_options['includes'] = []
prob.recording_options['record_objectives'] = True
prob.recording_options['record_constraints'] = True
prob.recording_options['record_desvars'] = True

prob.setup()
prob.run_driver()

prob.record('f')
prob.cleanup()

cr = om.CaseReader("cases_ex.sql")

# get list of cases recorded on problem
problem_cases = cr.list_cases('problem')