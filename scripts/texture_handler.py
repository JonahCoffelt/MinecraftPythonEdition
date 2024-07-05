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

        # Dictionary containing all texture's data. This is not the texture itself.
        self.textures = {size: [] for size in (128, 256, 512, 1024, 2048)}

        # Dictionary containing all texture arrays
        self.texture_arrays = {}


    def write_textures(self, program) -> None:
        #for i, array in enumerate((8, 16, 32)):
            #if not array in self.texture_arrays: continue
        program[f'textureArrays[0].array'] = 3
        self.texture_arrays[128].use(location=3)

    def generate_texture_arrays(self):
        for size in self.textures:
            data = []
            for texture in self.textures[size]:
                data.append(texture)
            data = np.array(data)
            self.texture_arrays[size] = self.ctx.texture_array((size, size, len(self.textures[size])), 3, data)
            # Mipmaps
            self.texture_arrays[size].filter = (mgl.NEAREST, mgl.NEAREST)
            self.texture_arrays[size].build_mipmaps()
            # AF
            self.texture_arrays[size].anisotropy = 32.0

    def load_texture(self, name: str, file: str) -> None:
        """
        Loads a texture in the project texture directory.
        If no directory was given on init, full path is expected in the file argument.
        File argument should include the file extension.
        """

        # Constructs the path based on file and directory
        if self.directory: path = self.directory + file
        else: path = file

        # Loads image using pygame
        texture = pg.image.load(path).convert()

        original_size = texture.get_size()[0]
        
        distances = np.array([abs(bucket_size - original_size) for bucket_size in self.textures.keys()])
        size = list(self.textures.keys())[np.argmin(distances)]

        texture = pg.transform.scale(texture, (size, size))
        texture = pg.transform.flip(texture, False, True)

        texture = self.ctx.texture(size=texture.get_size(), components=3, data = pg.image.tostring(texture, 'RGB'))

        data = texture.read()

        self.textures[size].append(data)

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