# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 19:15:44 2022

@author: renkert2
"""
import numpy as np
import shapely.geometry as SG
from shapely.affinity import affine_transform
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
from pprint import pprint
mpl.rcParams["image.aspect"] = "equal"
from ARG_Research_Python import my_plt



#%% Distance Check
polygon = SG.LinearRing([(0, 0), (1, 1), (1, 0)])
point = SG.Point(0.5, 1)
d = polygon.distance(point)
theta = np.arctan2(polygon.coords[1][1], polygon.coords[2][0])
R_from_prime = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
R_to_prime = np.linalg.inv(R_from_prime)
mat = [R_to_prime[0][0], R_to_prime[0][1], R_to_prime[1][0], R_to_prime[1][1], 0, 0]

(polygon_prime, point_prime) = [affine_transform(x, mat) for x in [polygon, point]]

print(d)

fig = plt.figure(0)
ax = fig.add_subplot()
ax.set_aspect('equal')

x,y = polygon.xy
plt.plot(x,y)

x,y = point.xy
plt.plot(x,y,'.r')

x,y = polygon_prime.xy
plt.plot(x,y)

x,y = point_prime.xy
plt.plot(x,y,'.r')

plt.show()

#%% 
polygon = SG.LinearRing([(0, 0), (1, 1), (1, 0)])
points = []
points.append(SG.Point(0.5, 1))
points.append(SG.Point(0.5, 0.25))
points.append(SG.Point(1,2))

fig = plt.figure(0)
ax = fig.add_subplot()
ax.set_aspect('equal')

x,y = polygon.xy
plt.plot(x,y)

for point in points:
    x,y = point.xy
    plt.plot(x,y, '.r')
    print(polygon.distance(point))

plt.show()

#%%

polygon = SG.LinearRing([(0, 0), (1, 1), (1, 0)])

def dist(polygon, X, Y):
    D = []
    P = []
    for i in range(len(X)):
        P_i = []
        D_i = []
        for j in range(len(X[i])):
            x = X[i][j]
            y = Y[i][j]
            p = SG.Point(x,y)
            P_i.append(p)
            D_i.append(polygon.distance(p))
        D.append(D_i)
        P.append(P_i)
    
    return D,P

x = np.linspace(0,1,4)
y = np.linspace(0,1,4)

X,Y = np.meshgrid(x,y)
#XYz = np.vstack([X.ravel(), Y.ravel()]).T
(D,P) = dist(polygon, X, Y)

pnt = [SG.Point((.5,1)), SG.Point((2,1))]
#print(dist(polygon, pnt))
    

#%%
polygon = SG.Polygon([(0, 0), (1, 1), (1, 0)])

def eff_length(box):
    dx = box[2] - box[0]
    dy = box[3] - box[1]
    eff_length = (np.abs(dx) + np.abs(dy))/2
    return eff_length



# Make outer boundary
box = polygon.bounds
poly_smooth = polygon.buffer(eff_length(box)*0.05)
poly_env = poly_smooth.envelope
poly_expand = poly_env.buffer(eff_length(box)*0.2, resolution=0, join_style=2, cap_style=3, mitre_limit=1000.0)
pbox = poly_expand.bounds

# Generate Grid
N = 50
X_pnts = np.linspace(pbox[0], pbox[2], N)
Y_pnts = np.linspace(pbox[1], pbox[3], N)

(X, Y) = np.meshgrid(X_pnts, Y_pnts)



def dist(polygon, X, Y):
    poly_ext = polygon.exterior
    D = np.zeros(np.shape(X))
    for i in range(len(X)):
        for j in range(len(X[i])):
            x = X[i][j]
            y = Y[i][j]
            p = SG.Point(x,y)
            d = poly_ext.distance(p)
            if polygon.contains(p):
                d = -d
            D[i][j] = d
    return D

Z = dist(poly_smooth, X, Y)

fig = plt.figure(0)
ax = plt.axes(projection='3d')
x,y = polygon.exterior.xy
ax.plot(x,y)

x,y = poly_smooth.exterior.xy
ax.plot(x,y)

ax.plot_surface(X, Y, Z, alpha=0.5, cmap = cm.coolwarm)

my_plt.export(fig, title="Padded Boundary Function Test")

plt.show()