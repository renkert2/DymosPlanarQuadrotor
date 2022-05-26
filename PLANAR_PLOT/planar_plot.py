import pyglet
import os
import components
import planar_sprite
import axes
import primitives
import cv2
import io
import numpy as np
from enum import Enum

class _Environment:
    def __init__(self, axes=axes.Axes(), ax_scale=0.7, width=900, height=900, caption="Planar Plot", batch=pyglet.shapes.Batch()):
        self.window = None
        
        self.axes = axes
        self.ax_scale = ax_scale
        
        self.width = width
        self.height = height
        self.caption = caption

        self._batch = batch

    def set_window(self, window):
        self.window = window
        self.init_graphics()

    def set_axes(self):
        self.axes._batch = self._batch

        scale_fact = self.ax_scale
        self.axes.width_img = scale_fact*self.window.width
        self.axes.height_img = scale_fact*self.window.height
        self.axes.center_at(self.window.width/2,self.window.height/2)
        self.axes.init_shapes()
    
    def init_graphics(self):
        self.set_axes()

    def draw(self):
        self._batch.draw()

class STEP(_Environment):
    def __init__(self):
        ax = axes.Axes(xlim=[0,10], ylim=[0,10])
        super().__init__(axes = ax,
                            ax_scale=0.7,
                            width=900,
                            height=900,
                            caption="Planar Plot: Step")

class MISSION_1(_Environment):
    def __init__(self):
        ax = axes.Axes(xlim=[0,21], ylim=[0,12])
        super().__init__(axes = ax,
                            ax_scale=0.85,
                            width=1300,
                            height=900,
                            caption="Planar Plot: Mission 1")

        self.waypoint_coords = [(0,0), (5,6), (15,2), (10,2), (10,10), (10,12)]
        self.waypoints_coords_win = None
        self.waypoints = None

        self.boundary_line_verts = [
            ((5,0), (5,5)),
            ((5,7), (5,10)),
            ((5,10), (9,10)),
            ((11,10), (20,10)),
            ((20,10), (20,0))
        ]
        self.boundary_lines = []
    
    def init_graphics(self):
        super().init_graphics()

        self.waypoints_coords_win = [self.axes._ax_to_window(x) for x in self.waypoint_coords]
        self.waypoints = primitives.Waypoints(coordinates = self.waypoints_coords_win, batch = self._batch, labels="index")
        for i in [2,5]:
            wp = self.waypoints._waypoints[i]
            wp._circle.color = primitives.Waypoint.STOP_COLOR

        self.boundary_lines = []
        for lverts in self.boundary_line_verts:
            lverts_win = [self.axes._ax_to_window(x) for x in lverts]
            line = pyglet.shapes.Line(*lverts_win[0], *lverts_win[1], width=5, color=(255, 0, 0), batch=self._batch)
            self.boundary_lines.append(line)

class PlanarPlot(components.Window):
    def __init__(self, env = STEP(), frame_rate = 60, playback_speed = 1, write=False, auto_close=True):
        super().__init__(height=env.height, width = env.width, caption = env.caption)
        self.env = env
        env.set_window(self)

        self.sprites = [] # List of PlanarSprites

        self.auto_close = auto_close
        self.duration_padding = 1.2
        self.duration = 0 # Duration of Animation
        self.playback_speed = playback_speed

        self.time = 0
        self.frame_rate = frame_rate

        if write:
            self.video_writer = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), self.frame_rate, (self.width,self.height))
        else:
            self.video_writer=None

    def write_frame(self):
        if self.video_writer:
            #buf = io.BytesIO()
            #pyglet.image.get_buffer_manager().get_color_buffer().save(filename="frame.png", file=buf)
            pyglet.image.get_buffer_manager().get_color_buffer().save(filename="frame.png")
            
            #img_frame = cv2.imdecode(np.frombuffer(buf.read(), np.uint8), cv2.IMREAD_COLOR)
            img_frame = cv2.imread("frame.png", cv2.IMREAD_COLOR)
            self.video_writer.write(img_frame)

    def on_draw(self):
        self.clear()
        self.env.draw()
        for sprite in self.sprites:
            sprite.draw()

        self.write_frame()
    
    def update(self, delta_t):
        self.time += delta_t
        for sprite in self.sprites:
            sprite.set_pose(self.time*self.playback_speed)
        
        self.write_frame()
        if self.auto_close and self.time > (self.duration)*self.duration_padding:
            self.close()
        
    def add_sprite(self, sprite):
        sprite.set_axes(self.env.axes)
        sprite.set_pose(self.time)
        self.sprites.append(sprite)
        self.duration = max(self.duration, sprite.time_bounds[1]/self.playback_speed)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            pyglet.clock.schedule_interval(self.update, 1/self.frame_rate)
        
        if symbol == pyglet.window.key.R:
            self.time = 0

    def close(self):
        print("Exiting via close")
        if self.video_writer:
            self.video_writer.release()
        super().close()

if __name__ == "__main__":
    import openmdao.api as om
    reader = om.CaseReader(os.path.join(os.path.dirname(__file__), "./ASSETS/input_opt_cases.sql"))
    case_init = reader.get_cases('problem')[0]
    case_final = reader.get_cases("problem")[-1]

    pp = PlanarPlot(env=MISSION_1(), auto_close=True, frame_rate=60, playback_speed=0.1, write=False)
    
    sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(255, 0, 0), width=2))
    sprite.set_traj(case_init)
    pp.add_sprite(sprite)

    sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(0, 255, 0), width=2))
    sprite.set_traj(case_final)
    pp.add_sprite(sprite)

    pyglet.app.run()

