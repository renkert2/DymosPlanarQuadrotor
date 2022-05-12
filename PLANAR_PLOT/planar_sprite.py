import pyglet

SPRITE_IMG_PATH = "./ASSETS/DRONE_FLAT_1.png"
SPRITE_IMG = pyglet.image.load(SPRITE_IMG_PATH)
SPRITE_IMG.anchor_x = 1106
SPRITE_IMG.anchor_y = SPRITE_IMG.height - 526

class PlanarSprite(pyglet.sprite.Sprite):
    def __init__(self, **kwargs):
        super().__init__(SPRITE_IMG, **kwargs)
        self.scale=0.1

    

if __name__ == "__main__":
    import components

    window = components.Window(resizable=True)

    sprite = PlanarSprite(x = window.width/2, y=window.height/2)

    @window.event
    def on_draw():
        window.clear()
        sprite.draw()

    pyglet.app.run()
