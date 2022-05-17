import pyglet
import pyglet.gl as gl
import pyglet.shapes as shapes
import numpy as np


def SmoothConfig():
    config = gl.Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)                                                                                      
    gl.glEnable(gl.GL_LINE_SMOOTH)                                                    
    gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
    return config

class Window(pyglet.window.Window):
    def __init__(self, **kwargs):
        if "config" not in kwargs:
            kwargs["config"] = SmoothConfig()
        super().__init__(**kwargs)

        self._clear_color = (0.2,0.2,0.2,1)
    
    def clear(self, *args, **kwargs):
        gl.glClearColor(*self._clear_color) # Note that these are values 0.0 - 1.0 and not (0-255).
        super().clear(*args, **kwargs)

if __name__ == "__main__":
    window = Window(width=1920, height=1080)

    @window.event
    def on_draw():
        window.clear()

    pyglet.app.run()