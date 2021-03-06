"""
Simple example showing some animated shapes
"""
import math
import pyglet
from pyglet import shapes
from pyglet.gl import *


class MultiLine(shapes._ShapeBase):
    def __init__(self, *coordinates, color=(255, 255, 255), width=1, batch=None, group=None):
        self._coordinates = list(coordinates)

        self._rotation = 0

        self._rgb = color
        self._width = width

        self._batch = batch or shapes.Batch()
        self._group = shapes._ShapeGroup(shapes.GL_SRC_ALPHA, shapes.GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add(self._num_verts, GL_LINES, self._group, 'v2f', 'c4B')
        self._update_position()
        self._update_color()
    
    @property
    def _num_segs(self):
        return len(self._coordinates) - 1

    @property
    def _num_verts(self):
        return self._num_segs * 2

    def append(self, coord):
        self._coordinates.append(coord)
        self._vertex_list.resize(self._num_verts)
        self._update_position()
        self._update_color()

    def _update_position(self):
        if not self._visible:
            self._vertex_list.vertices = (0,) * self._num_segs * 4 # ?
        else:
            points = self._coordinates

            vertices = []
            for i in range(len(points) - 1):
                line_points = *points[i], *points[i+1]
                vertices.extend(line_points)

            self._vertex_list.vertices[:] = vertices
        pass
    def _update_color(self):
        self._vertex_list.colors[:] = [*self._rgb, int(self._opacity)] * self._num_verts

    @property
    def rotation(self):
        """Clockwise rotation of the arc, in degrees.

        The arc will be rotated about its (anchor_x, anchor_y)
        position.

        :type: float
        """
        return self._rotation

    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation
        self._update_position()

    def draw(self):
        """Draw the shape at its current position.

        Using this method is not recommended. Instead, add the
        shape to a `pyglet.graphics.Batch` for efficient rendering.
        """
        #w_cache = (pyglet.gl.GLint*1)()
        #pyglet.gl.glGetIntegerv("GL_LINE_WIDTH", w_cache)
        w_cache = 1
        pyglet.gl.glLineWidth(self._width)
        self._vertex_list.draw(GL_LINES)
        pyglet.gl.glLineWidth(w_cache)

class ShapesDemo(pyglet.window.Window):
    def __init__(self, width, height, **kwargs):
        super().__init__(width, height, "Shapes", **kwargs)
        self.time = 0
        self.batch = pyglet.graphics.Batch()

        coordinates = [(0,0), (400,100), (200,200)]
        self.polygon = MultiLine(*coordinates, color=(255, 255, 255), batch=self.batch, width=5)
        self.polygon.append((500,400))

        self.line = shapes.Line(0, 0, 720, 480, width=4, color=(200, 20, 20), batch=self.batch)

        self.arc = shapes.Arc(width/2,height/2,200, color=(0,255,0), angle=math.pi, batch=self.batch)

    def on_draw(self):
        """Clear the screen and draw shapes"""
        #self.clear()
        #self.batch.draw()
        self.line.draw()
        self.polygon.draw()
        self.arc.draw()
        self.line.draw()


if __name__ == "__main__":
    config = Config(sample_buffers=1, samples=4, depth_size=16, double_buffer=True)                                                                                      
    glEnable(GL_LINE_SMOOTH)                                                    
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    demo = ShapesDemo(720, 480, config=config)
    pyglet.app.run()
