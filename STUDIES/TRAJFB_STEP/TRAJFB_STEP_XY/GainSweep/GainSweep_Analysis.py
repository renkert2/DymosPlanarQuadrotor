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
plt.plot(gain_vals, obj_vals, label="Sweep Values")
plt.xlabel("Position Proportional Gain")
plt.ylabel("Accum. Tracking Error")

# Annotate
plt.axvline(9.16372, c='r', ls='--', label="Initial Gain: 1")
plt.axvline(11.21, c='g',ls='--', label="Initial Gain: 10")
plt.legend()
plt.show()

my_plt.export(plt.gcf(), fname="gain_sweep_singlevar")

#%%
obj_diff = np.gradient(obj_vals, gain_vals)

plt.plot(gain_vals, obj_diff)
plt.xlabel("Position Proportional Gain")
plt.ylabel("Accum. Tracking Error Derivative")
plt.axhline(0, ls="--",c='r')
plt.show()
my_plt.export(plt.gcf(), fname="gain_sweep_gradient")

#%% Plot Actuator Saturation for Various Gains

(fig,ax) = plt.subplots()
for (case, gain) in zip(cases, gain_vals):
    if (gain == 6 or gain == 7):
        t_vals = case.get_val("traj.phases.phase0.timeseries.time")
        omega_star_vals = case.get_val("traj.phases.phase0.timeseries.CTRL_omega_1_star")
        e_omega_1 = case.get_val("traj.phases.phase0.timeseries.CTRL_e_omega_1")
        e_omega_1_I = case.get_val("traj.phases.phase0.timeseries.states:CTRL_e_omega_1_I")
        
        u_1 = case.get_val("traj.phases.phase0.timeseries.CTRL_u_1")
        
        k_p_omega = case.get_val("params.k_p_omega__Controller")
        k_i_omega = case.get_val("params.k_i_omega__Controller")
        u_1_star = -k_p_omega*e_omega_1 - k_i_omega*e_omega_1_I
        
        if gain >= 6.5:
            color = 'r'
        else:
            color = 'g'
        
        ax.plot(t_vals, u_1_star, label=f"Gain: {gain}", color=color, alpha=(gain/max(gain_vals))**2)

#ax.set_ylim([0.95  ,1])
ax.set_xlabel("Time (s)")
ax.set_ylabel("Input 1")
plt.show()

#my_plt.export(fig, fname="gain_sweep_input_saturation")