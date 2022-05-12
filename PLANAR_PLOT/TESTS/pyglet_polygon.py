"""
Simple example showing some animated shapes
"""
import math
import pyglet
from pyglet import shapes
from pyglet.gl import GL_LINES


class MultiLine(shapes._ShapeBase):
    def __init__(self, *coordinates, color=(255, 255, 255), batch=None, group=None):
        self._coordinates = list(coordinates)

        self._rotation = 0

        self._rgb = color

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
        self._vertex_list.draw(GL_LINES)

class ShapesDemo(pyglet.window.Window):

    def __init__(self, width, height):
        super().__init__(width, height, "Shapes")
        self.time = 0
        self.batch = pyglet.graphics.Batch()

        coordinates = [(0,0), (400,100), (200,200)]
        self.polygon = MultiLine(*coordinates, color=(255, 255, 255), batch=self.batch)
        self.polygon.append((500,400))

        self.line = shapes.Line(0, 0, 720, 480, width=4, color=(200, 20, 20), batch=self.batch)

        self.arc = shapes.Arc(width/2,height/2,200, color=(0,255,0), angle=math.pi, batch=self.batch)

    def on_draw(self):
        """Clear the screen and draw shapes"""
        self.clear()
        self.batch.draw()


if __name__ == "__main__":
    demo = ShapesDemo(720, 480)
    pyglet.app.run()
