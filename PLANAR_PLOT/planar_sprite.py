import pyglet
from scipy import interpolate
import numpy as np
import os

SPRITE_IMG_PATH = os.path.join(os.path.dirname(__file__), "./ASSETS/DRONE_FLAT_1.png")
SPRITE_IMG = pyglet.image.load(SPRITE_IMG_PATH)
SPRITE_IMG.anchor_x = 1106
SPRITE_IMG.anchor_y = SPRITE_IMG.height - 526

class PlanarSprite(pyglet.sprite.Sprite):
    def __init__(self, trace=None, **kwargs):
        super().__init__(SPRITE_IMG, **kwargs)
        self.scale=0.1

        self.trajectory = None
        self.time_bounds = None
        self.s_x = None
        self.s_y = None
        self.s_theta = None

        self.axes = None
        self.trace = trace
    
    def set_traj(self, case):
        t = case.get_val('traj.phase0.timeseries.time').flatten()
        t,i = np.unique(t, return_index=True)

        self.time_bounds = (t[0], t[-1])

        x = case.get_val('traj.phase0.timeseries.states:BM_x').flatten()[i]
        y = case.get_val('traj.phase0.timeseries.states:BM_y').flatten()[i]
        theta = case.get_val('traj.phase0.timeseries.states:BM_theta').flatten()[i]

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
