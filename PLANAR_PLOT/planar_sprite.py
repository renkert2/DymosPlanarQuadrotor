import pyglet
from scipy import interpolate
import numpy as np
import os

SPRITE_IMG_PATH = os.path.join(os.path.dirname(__file__), "./ASSETS/DRONE_FLAT_1.png")
SPRITE_IMG = pyglet.image.load(SPRITE_IMG_PATH)
SPRITE_IMG.anchor_x = 1106
SPRITE_IMG.anchor_y = SPRITE_IMG.height - 526
SPRITE_WIDTH = 0.48 #m

class PlanarSprite(pyglet.sprite.Sprite):
    def __init__(self, trace=None, **kwargs):
        super().__init__(SPRITE_IMG, **kwargs)
        self.scale=0.1
        self.scale_multiplier = 7
        self.width_m = SPRITE_WIDTH

        self.trajectory = None
        self.time_bounds = None
        self.s_x = None
        self.s_y = None
        self.s_theta = None

        self.axes = None
        self.trace = trace

    def set_axes(self, ax):
        self.axes = ax
        self.set_scale()
    
    def set_scale(self):
        ax = self.axes
        ax_range = max(self.axes.xlim) - min(self.axes.xlim)
        ax_width = ax.width_img
        sprite_img_width = SPRITE_IMG.width

        s = (self.width_m*ax_width)/(ax_range*sprite_img_width)
        s = s*self.scale_multiplier
        self.scale = s

    def set_traj(self, case, phases=["phase0"]):
        if not isinstance(phases, (list,tuple)):
            phases = [phases]

        def  _get_val(case, paths):
            val_arrays = []
            for p in paths:
                val = case.get_val(p).flatten()
                val_arrays.append(val)
        
            val_cat = np.concatenate(val_arrays)
            return val_cat

        t = _get_val(case,[f'traj.{p}.timeseries.time' for p in phases])
        t,i = np.unique(t, return_index=True)

        self.time_bounds = (t[0], t[-1])

        x = _get_val(case, [f'traj.{p}.timeseries.states:BM_x' for p in phases])[i]
        y = _get_val(case, [f'traj.{p}.timeseries.states:BM_y' for p in phases])[i]
        theta = _get_val(case, [f'traj.{p}.timeseries.states:BM_theta' for p in phases])[i]

        spline_opts = {"k":3, "ext":3}
        self.s_x = interpolate.InterpolatedUnivariateSpline(t,x, **spline_opts)
        self.s_y = interpolate.InterpolatedUnivariateSpline(t,y, **spline_opts)
        self.s_theta = interpolate.InterpolatedUnivariateSpline(t,theta, **spline_opts)

        pose = zip(x,y,theta)
        traj = list(zip(t,pose))

        self.trajectory = traj
        return traj
    
    def interp_pose(self, time):
        x = self.s_x(time)
        y = self.s_y(time)
        theta = self.s_theta(time)

        return np.array((x,y,theta))

    def set_pose(self, time):
        if self.time_bounds[0] <= time <= self.time_bounds[1]:
            pose_ax = self.interp_pose(time)

            r_ax = pose_ax[:2]
            if self.axes:
                r_win = self.axes._ax_to_window(r_ax)
            else:
                r_win = r_ax
            
            theta_win = pose_ax[-1]*(-180/np.pi) # Convert to clockwise rotation in degrees
            
            self.update(x=r_win[0], y=r_win[1], rotation=theta_win)
            
            if self.trace:
                self.trace.append(r_win)

            return (*r_win, theta_win)
    
    def draw(self, *args, **kwargs):
        if self.trace:
            self.trace.draw()
        
        return super().draw(*args, **kwargs)

if __name__ == "__main__":
    import components

    window = components.Window(resizable=True)

    sprite = PlanarSprite(x = window.width/2, y=window.height/2)

    @window.event
    def on_draw():
        window.clear()
        sprite.draw()

    pyglet.app.run()
