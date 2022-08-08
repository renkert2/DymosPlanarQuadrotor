#%%
import openmdao.api as om
import SUPPORT_FUNCTIONS.plotting as plotting
import my_plt
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.init as init
import os
import numpy as np

init.init_output(__file__)

name="gain_sweep_cases"
reader = om.CaseReader(name+".sql")
cases = reader.get_cases("problem")

#%%
gain_vals = []
obj_vals = []
for c in cases:
    gain_vals.append(c.get_val("params.k_p_r__Controller")[0])
    obj_vals.append(c.get_val('traj.phase0.states:CTRL_e_T_I', indices=[-1])[0][0])
    
#%%
plt.plot(gain_vals, obj_vals)
plt.xlabel("Position Proportional Gain")
plt.ylabel("Accum. Tracking Error")
plt.show()
my_plt.export(plt.gcf(), fname="gain_sweep")

#%%
obj_diff = np.gradient(obj_vals, gain_vals)

plt.plot(gain_vals, obj_diff)
plt.xlabel("Position Proportional Gain")
plt.ylabel("Accum. Tracking Error Derivative")
plt.axhline(0, ls="--",c='r')
plt.show()
my_plt.export(plt.gcf(), fname="gain_sweep_gradient")