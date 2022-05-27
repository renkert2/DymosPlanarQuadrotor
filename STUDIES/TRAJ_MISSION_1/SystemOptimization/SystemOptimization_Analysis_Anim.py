# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search
import matplotlib.pyplot as plt
import numpy as np
import pyglet

import PlanarSystem as PS
import Recorders as R
import PLANAR_PLOT.planar_plot as planar_plot
import PLANAR_PLOT.planar_sprite as planar_sprite
import PLANAR_PLOT.primitives as primitives

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__)

import weekly_reports
wdir = weekly_reports.find_dir("06012022")[-1]

name = "sys_opt_cases"
sim_name= name+"_sim"

reader = R.Reader(name+".sql")
cases = reader.get_cases("problem")
base_case = cases[0]
final_case = cases[1]

pp = planar_plot.PlanarPlot(env=planar_plot.MISSION_1(), auto_close=False, frame_rate=30, playback_speed=1, write=False)

sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(255, 0, 0), width=2))
sprite.set_traj(base_case, phases=[f"phase{i}" for i in range(5)])
pp.add_sprite(sprite)

sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(0, 255, 0), width=2))
sprite.set_traj(final_case, phases=[f"phase{i}" for i in range(5)])
pp.add_sprite(sprite)

pyglet.app.run()