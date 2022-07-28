# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 15:30:24 2022

@author: renkert2
"""
import os
import openmdao.api as om
import dymos as dm
import PlanarSystem as ps
import PlanarController.PlanarController as pc


def checkProblem(p):
        p.setup()
        p.final_setup()
        #om.n2(p, outfile="n2_prerun.html")
        p.run_model()
    
        # Visualize:
        om.n2(p)
        #om.view_connections(p)
        
        # Checks:
        #p.check_config(out_file=os.path.join(os.getcwd(), "openmdao_checks.out"))
        p.check_partials(compact_print=True, show_only_incorrect=True)
        p.cleanup()
        
        # Print Constraints
        print(p.list_problem_vars())

os.chdir(os.path.dirname(__file__))
if not os.path.isdir('./PlanarSystemDAE_PlanarController/'):
    os.mkdir('./PlanarSystemDAE_PlanarController/')
os.chdir('./PlanarSystemDAE_PlanarController/')

p = om.Problem(model=ps.PlanarSystemDAE(num_nodes = 10, include_controller=True))
checkProblem(p)


os.chdir(os.path.dirname(__file__))   
if not os.path.isdir('./PlanarSystemModel_PlanarController/'):
    os.mkdir('./PlanarSystemModel_PlanarController/')
os.chdir('./PlanarSystemModel_PlanarController/')
    
nn = 20
tx = dm.GaussLobatto(num_segments=nn)
phase = ps.PlanarSystemDynamicPhase(transcription=tx, include_controller=True)
phase.init_vars()

traj = ps.PlanarSystemDynamicTraj(phase)
traj.init_vars()

sys = ps.PlanarSystemModel(traj)
p = om.Problem(model=sys)

checkProblem(p)