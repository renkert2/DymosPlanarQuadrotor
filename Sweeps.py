# -*- coding: utf-8 -*-
"""
Created on Wed Mar 23 14:56:36 2022

@author: renkert2
"""
import Recorders as R
import matplotlib.pyplot as plt
import SUPPORT_FUNCTIONS.plotting as my_plt

def simple_sweep(prob, sweep_param, vals):
    prob = R.SimpleRecorder(prob, name=f"{sweep_param}_sweep_cases.sql")
    print(f"Running {sweep_param} Sweep")
    for val in vals:
        prob.set_val(f'params.{sweep_param}', val)
        print(f"Solving optimization for {sweep_param} = {val}")
        prob.run_model()
        # Check Thrust Ratio for Feasibility
        tr = prob.get_val("constraint__thrust_ratio.TR")
        print(f"Thrust Ratio: {tr}")
        if tr <= 1 or tr >= 10:
            print("Infeasible Thrust Ratio")
        else:
            failed = prob.run_driver(case_prefix=f"{sweep_param}_{val}")
            if not failed:
                prob.record(f"{sweep_param}_{val}")
            else:
                print("Driver Failed")
    prob.cleanup()
    
def plot_sweeps(cases, sweep_param, out_paths):
    in_vals = []
    out_vals = []
    for case in cases:
        in_vals.append(case.get_val(f"params.{sweep_param}"))
        out_vals.append([case.get_val(x) for x in out_paths])
    
    fig, axes = plt.subplots(len(out_paths), 1)
    for (i,ax) in enumerate(axes):
        out = [x[i] for x in out_vals]
        ax.plot(in_vals, out)

    return (fig, axes)