# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 19:15:44 2022

@author: renkert2
"""

import shapely.geometry as SG

polygon = SG.LinearRing([(0, 0), (1, 1), (1, 0)])
point = SG.Point(0.5, 2)

d = polygon.distance(point)

print(d)
