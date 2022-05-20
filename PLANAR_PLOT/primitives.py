import pyglet.shapes as shapes
import pyglet.gl as gl
import pyglet

class Waypoint:
    def __init__(self, coordinate=None, label=None, batch = shapes.Batch()):
        self._batch = batch

        self._background = pyglet.graphics.OrderedGroup(0)
        self._forground = pyglet.graphics.OrderedGroup(1)
        
        self._coordinate = coordinate
        self._label_txt = label

        self._circle = None
        self._label = None
    
    def init_graphics(self):
        self._circle = shapes.Circle(*self._coordinate, radius=20, color=(0,191,255), batch=self._batch, group=self._background)
        self._label = pyglet.text.Label(x=self._coordinate[0], y=self._coordinate[1], text=self._label_txt, font_name="Times New Roman", bold=True, font_size=20, anchor_x='center', anchor_y='center', batch=self._batch, group=self._forground)

    def draw(self):
        self._batch.draw()

class Waypoints:
    def __init__(self, coordinates = [], batch = shapes.Batch(), labels="index"):
        self._batch = batch

        self._coordinates = coordinates
        self._waypoints = []

        self.labels=labels

        self.init_graphics()
    
    def init_graphics(self):
        if self.labels == "index":
            labels = range(len(self._coordinates))
        else:
            labels = self.labels

        self._waypoints = []
        for (coord, label) in zip(self._coordinates, labels):
            wp = Waypoint(coordinate=coord, label=str(label), batch=self._batch)
            wp.init_graphics()
            self._waypoints.append(wp)

    def draw(self):
        self._batch.draw()


class MultiLine:
    def __init__(self, color=(255, 255, 255), width=1, batch=None):
        self._rgb = color
        self._width = width

        self._batch = batch or shapes.Batch()

        self._coordinates = []
        self._line_list = []
    
    def append(self, coord):
        self._coordinates.append(coord)
        if len(self._coordinates) > 1:
            coord_prev = self._coordinates[-2]
            line = shapes.Line(*coord_prev, *coord, width=self._width, color=self._rgb, batch=self._batch)
            self._line_list.append(line)
    
    def draw(self):
        self._batch.draw()

class MultiLineGL(shapes._ShapeBase):
    def __init__(self, coordinates = [], color=(255, 255, 255), width=1, batch=None, group=None):
        self._coordinates = coordinates

        self._rotation = 0

        self._rgb = color
        self._width = width

        self._batch = batch or shapes.Batch()
        self._group = shapes._ShapeGroup(shapes.GL_SRC_ALPHA, shapes.GL_ONE_MINUS_SRC_ALPHA, group)

        if coordinates:
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
        if not self._vertex_list:
            self._vertex_list = self._batch.add(self._num_verts, gl.GL_LINES, self._group, 'v2f', 'c4B')
        else:
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
    batch = shapes.Batch()

    coordinates = [(0,0), (400,100), (200,200)]
    polygon = MultiLine(color=(0, 255, 0), width=2, batch=batch)
    for c in coordinates:
        polygon.append(c)

    coordinates_2 = [(10,10), (410,110), (210,210)]
    polygon_2 = MultiLine(color=(255, 0, 0), width=2, batch=batch)
    for c in coordinates_2:
        polygon_2.append(c)

    polygon.append((100,100))
    polygon_2.append((110,110))

    wpt_coords = [(100*i, 50*i) for i in range(5)]
    waypoints = Waypoints(coordinates=wpt_coords, batch=batch)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    
    pyglet.app.run()