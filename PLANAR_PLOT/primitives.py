import pyglet.shapes as shapes
import pyglet.gl as gl

class MultiLine(shapes._ShapeBase):
    def __init__(self, *coordinates, color=(255, 255, 255), width=1, batch=None, group=None):
        self._coordinates = list(coordinates)

        self._rotation = 0

        self._rgb = color
        self._width = width

        self._batch = batch or shapes.Batch()
        self._group = shapes._ShapeGroup(shapes.GL_SRC_ALPHA, shapes.GL_ONE_MINUS_SRC_ALPHA, group)

        self._vertex_list = self._batch.add(self._num_verts, gl.GL_LINES, self._group, 'v2f', 'c4B')
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
        gl.glLineWidth(self._width)
        self._vertex_list.draw(gl.GL_LINES)
        gl.glLineWidth(w_cache)

if __name__ == "__main__":
    import components
    import pyglet

    window = components.Window(width=720, height=480, caption="Primitives")

    coordinates = [(0,0), (400,100), (200,200)]
    polygon = MultiLine(*coordinates, color=(255, 255, 255), width=5)
    polygon.append((500,400))

    line = shapes.Line(0, 0, 720, 480, width=4, color=(200, 20, 20))
    arc = shapes.Arc(720/2,480/2,200, color=(0,255,0), angle=3.14)

    @window.event
    def on_draw():
        window.clear()

        polygon.draw()
        line.draw()
        arc.draw()
    
    pyglet.app.run()