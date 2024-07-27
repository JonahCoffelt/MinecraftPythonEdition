import pygame as pg
import numpy as np
import moderngl as mgl


class TextureHandler:
    def __init__(self, engine, directory: str='textures/') -> None:
        # Stores the engine and context
        self.engine = engine
        self.ctx = self.engine.ctx

        # The folder containing all textures for the project
        self.directory = directory

        # List containing all textures
        self.textures = []

        self.texture_surfaces = []

        self.texture_array = None
        self.size = 8

        self.framebuffer = None
        self.generate_frame_buffer()


    def write_textures(self, program) -> None:
        program[f'textureArray'] = 3
        if self.texture_array: self.texture_array.use(location=3)

    def generate_texture_arrays(self):
        data = []
        for texture in self.textures:
            data.append(texture.read())
        data = np.array(data)
        self.texture_array = self.ctx.texture_array((self.size, self.size, len(self.textures)), 3, data)
        # Mipmaps
        texture.build_mipmaps()
        self.texture_array.filter = (mgl.NEAREST, mgl.NEAREST)
        #self.texture_array.build_mipmaps()
        # AF
        self.texture_array.anisotropy = 32.0

    def load_texture(self, file: str) -> None:
        """
        Loads a texture in the project texture directory.
        If no directory was given on init, full path is expected in the file argument.
        File argument should include the file extension.
        """

        # Constructs the path based on file and directory
        if self.directory: path = self.directory + file
        else: path = file

        # Loads image using pygame
        texture = pg.image.load(path).convert_alpha()
        texture = pg.transform.scale(texture, (self.size, self.size))

        # Add to the surfaces list
        self.texture_surfaces.append(texture)

        # Create and save an MGL texture
        texture = self.ctx.texture(size=texture.get_size(), components=3, data = pg.image.tostring(texture, 'RGB'))
        self.textures.append(texture)

    def generate_frame_buffer(self):
        """
        Creates a texture for the frame to be rendered to before going to the screen
        """
        
        if self.framebuffer: self.framebuffer.release()

        size = self.engine.win_size
        self.depth_texture = self.ctx.depth_texture(size)
        self.frame_texture = self.ctx.texture(size, 4, dtype='f4')

        self.framebuffer = self.ctx.framebuffer([self.frame_texture], self.depth_texture)

    def set_directory(self, directory: str=None) -> None:
        """
        Changes the directory of textures to be loaded
        """

        self.directory = directory

    def release(self) -> None:
        """
        Releases all textures in a project
        """

        [tex.release() for tex in self.textures.values()]