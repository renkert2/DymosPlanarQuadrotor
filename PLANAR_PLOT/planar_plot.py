import pyglet
import os
import components
import planar_sprite
import axes
import primitives
import cv2
import io
import numpy as np

class PlanarPlot(components.Window):
    def __init__(self, frame_rate = 60, playback_speed = 1, write=False, auto_close=True):
        super().__init__(width=900, height=900, caption="Planar Plot")

        self.axes = axes.Axes()
        self.axes.xlim = [0,10]
        self.axes.ylim = [0,10]
        scale_fact = 0.7
        self.axes.width_img = scale_fact*self.width
        self.axes.height_img = scale_fact*self.height
        self.axes.center_at(self.width/2,self.height/2)
        self.axes.init_shapes()

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
        self.axes.draw()
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
        sprite.axes = self.axes
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

    pp = PlanarPlot(auto_close=True, frame_rate=60, playback_speed=0.1, write=False)
    
    sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(255, 0, 0), width=2))
    sprite.set_traj(case_init)
    pp.add_sprite(sprite)

    sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(0, 255, 0), width=2))
    sprite.set_traj(case_final)
    pp.add_sprite(sprite)

    pyglet.app.run()

