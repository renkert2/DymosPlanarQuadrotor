# -*- coding: utf-8 -*-
"""
Created on Thu May  5 08:43:02 2022

@author: renkert2
"""

from msilib.schema import Directory
import os
import pickle
import openmdao.api as om
import SUPPORT_FUNCTIONS.init as init
import OPTIM.Search as search
import matplotlib.pyplot as plt
import numpy as np
import pyglet

import PlanarSystem as PS
import PLANAR_PLOT.planar_plot as planar_plot
import PLANAR_PLOT.planar_sprite as planar_sprite
import PLANAR_PLOT.primitives as primitives

import logging
logging.basicConfig(level=logging.INFO)

init.init_output(__file__, dirname="Output_07052022")
reader = search.SearchReader(output_dir = "search_output")

#%% Read Search Result
result = reader.result
print(result)

#%%
case_reader = reader.case_reader

base_case = case_reader.get_case("base_case")
final_case = case_reader.get_case(result.opt_iter.case_name)


pp = planar_plot.PlanarPlot(env=planar_plot.MISSION_1(), auto_close=True, frame_rate=30, update_rate=0.5, playback_speed=0.25, write=True, outfile_name="planar_plot.avi")

sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(255, 0, 0), width=2))
sprite.set_traj(base_case)
pp.add_sprite(sprite)

sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(0, 255, 0), width=2))
sprite.set_traj(final_case)
pp.add_sprite(sprite)

pyglet.app.run()