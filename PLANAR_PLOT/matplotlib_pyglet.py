from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import io

import pyglet

import components

def render_figure(fig):
    w, h = fig.get_size_inches()
    dpi_res = fig.get_dpi()
    w, h = int(np.ceil(w * dpi_res)), int(np.ceil(h * dpi_res))

    canvas = FigureCanvasAgg(fig)
    data, (w, h) = canvas.print_to_buffer()
    return pyglet.image.ImageData(w, h, "RGBA", data, -4 * w)

if __name__ == "__main__":
    window = components.Window(width=720, height=480)

    dpi_res = min(window.width, window.height) / 10
    fig = Figure((window.width / dpi_res, window.height / dpi_res), dpi=dpi_res)

    draw_figure(fig)
    image = render_figure(fig)


    @window.event
    def on_draw():
        window.clear()
        image.blit(0, 0)


    pyglet.app.run()

