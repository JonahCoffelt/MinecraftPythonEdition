import pygame as pg
import moderngl as mgl


class UIHandler:
    def __init__(self, ctx, win_size=(800, 800)) -> None:
        # Save refernece to context
        self.ctx = ctx

        # Save the window size
        self.win_size = win_size

        # Create a surface for the UI
        self.surf = pg.Surface(self.win_size).convert_alpha()

        # Variables for updating
        self.update_texture = True

    def use(self, scene, frame_vao, win_size=(800, 800)):
        # Save refernece to parent scene and frame vao
        self.scene = scene
        self.frame_vao = frame_vao

        self.resize(win_size)

    def resize(self, win_size):
        """
        Resize the surface and texture if the window is resized
        """
        
        # Save the window size
        self.win_size = win_size

        # Create a surface for the UI
        self.surf = pg.Surface(win_size).convert_alpha()

        # Create a surface for the UI
        self.surf = pg.Surface(self.win_size).convert_alpha()

        # Generate an empty texture for the UI
        self.generate_ui_texture()

        # Variables for updating
        self.update_texture = True


    def generate_ui_texture(self):
        """
        Generates a blank texture for writing the UI surface
        """
        
        self.texture = self.ctx.texture(self.surf.get_size(), 4)
        self.texture.filter = (mgl.NEAREST, mgl.NEAREST)
        self.texture.swizzel = 'BGRA'

    def surf_to_texture(self):
        """
        Converts the UI surface to a texture
        """
        
        self.texture.write(self.surf.get_view('1'))

    def write_texture(self):
        """
        Writes the UI texture as is to the frame vao program
        """
        
        self.frame_vao.program['uiTexture'] = 1
        self.texture.use(location=1)
        
        self.update_texture = False

    def update(self):
        """
        If the UI needs to be updated, will draw and write the the texture
        """
        
        if not self.update_texture: return
        
        self.draw()
        self.surf_to_texture()
        self.write_texture()

    def draw(self):
        """
        Draws all pygame elements to the UI
        """
        
        self.surf.fill((0, 0, 0, 0))

        cross_len = 20
        cross_width = 3
        pg.draw.rect(self.surf, (225, 225, 225, 155), (self.win_size[0]/2 - cross_len/2  , self.win_size[1]/2 - cross_width/2, cross_len, cross_width))
        pg.draw.rect(self.surf, (225, 225, 225, 155), (self.win_size[0]/2 - cross_width/2, self.win_size[1]/2 - cross_len/2  , cross_width, cross_len))