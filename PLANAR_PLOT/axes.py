import pyglet
import pyglet.gl as gl
import pyglet.shapes as shapes
import numpy as np
import components

class Axes:
    def __init__(self, xlim=[0,10], ylim=[0,10], width_img=720, height_img=480, origin_img=(0,0), batch=pyglet.graphics.Batch()):
        self.xlim = xlim
        self.ylim = ylim

        self.width_img = width_img # Pixels
        self.height_img = height_img # Pixels
        self.origin_img = origin_img # Origin of Axis in Window Coordinates

        self._batch = batch

    def init_shapes(self):
        line_width = 5
        s2w = self._scaled_to_window
        corners = {}
        corners["NW"] = s2w((1,0))
        corners["SE"] = s2w((0,1))
        corners["NE"] = s2w((1,1))
        self.x_line = shapes.Line(*self.origin_img, *corners["NW"], width=line_width, batch=self._batch)
        self.y_line = shapes.Line(*self.origin_img, *corners["SE"], width=line_width, batch=self._batch)
        self.origin_rect = shapes.Rectangle(*self.origin_img, line_width, line_width, batch=self._batch)
        self.origin_rect.anchor_x = line_width/2
        self.origin_rect.anchor_y = line_width/2

        text_opts = {"font_name":"CMU Serif", "font_size":20, "bold":True, "italic":True, "anchor_x":'center', "anchor_y":'center', "batch":self._batch}
        label_margin = 2*text_opts["font_size"]/2
        x_label_pos = s2w((0.5,0))
        self.x_label = pyglet.text.Label(text="x", x=x_label_pos[0], y=x_label_pos[1] - label_margin, **text_opts)
        y_label_pos = s2w((0,0.5))
        self.y_label = pyglet.text.Label(text="y", x=y_label_pos[0] - label_margin, y=y_label_pos[1], **text_opts)

    def draw(self):
        self._batch.draw()

    def update(self):
        pass

    def center_at(self, x_cent, y_cent):
        x_origin = x_cent - self.width_img/2
        y_origin = y_cent - self.height_img/2

        self.origin_img = (x_origin, y_origin)

    def _ax_to_scaled(self, point_ax):
        point_axes = np.array(point_ax)
        point_scaled = np.zeros((2,))

        # Scale so the j_min, j_max :-> (0,1)
        point_scaled[0] = (point_axes[0] - self.xlim[0])/self.xlim[1]
        point_scaled[1] = (point_axes[1] - self.ylim[0])/self.ylim[1]

        return tuple(point_scaled)

    def _scaled_to_window(self, point_scaled):
        point_scaled = np.array(point_scaled)

        # Scale to _img coordinates
        point_window = np.array(self.origin_img) + point_scaled*np.array((self.width_img, self.height_img))

        return tuple(point_window)
    
    def _ax_to_window(self, point_ax):
        return self._scaled_to_window(self._ax_to_scaled(point_ax))

if __name__ == "__main__":
    window = components.Window(width=720, height=480)
    ax = Axes()
    ax.origin_img = (100,100)
    ax.width_img = 500
    ax.height_img = 300
    ax.init_shapes()

    @window.event
    def on_draw():
        window.clear()
        ax.draw()


    pyglet.app.run()