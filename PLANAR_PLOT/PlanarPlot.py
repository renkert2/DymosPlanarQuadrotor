import pyglet
import components
import planar_sprite
import axes
import primitives

class PlanarPlot(components.Window):
    def __init__(self, *args, **kwargs):
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

        self.time = 0

    def on_draw(self):
        self.clear()
        self.axes.draw()
        for sprite in self.sprites:
            sprite.draw()
    
    def update(self, delta_t):
        self.time += delta_t
        for sprite in self.sprites:
            sprite.set_pose(self.time)
        
    def add_sprite(self, sprite):
        sprite.axes = self.axes
        sprite.set_pose(self.time)
        self.sprites.append(sprite)


if __name__ == "__main__":
    import openmdao.api as om
    reader = om.CaseReader("./ASSETS/input_opt_cases.sql")
    case_init = reader.get_cases('problem')[0]
    case_final = reader.get_cases("problem")[-1]

    pp = PlanarPlot()

    sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(255, 0, 0), width=2))
    sprite.set_traj(case_init)
    pp.add_sprite(sprite)

    sprite = planar_sprite.PlanarSprite(trace=primitives.MultiLine(color=(0, 255, 0), width=2))
    sprite.set_traj(case_final)
    pp.add_sprite(sprite)

    pyglet.clock.schedule_interval(pp.update, 1/60)
    pyglet.app.run()

