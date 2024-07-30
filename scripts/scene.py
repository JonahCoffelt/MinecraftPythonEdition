from scripts.player import Player
from scripts.camera import *
from scripts.chunk_handler import ChunkHandler
from scripts.item_entity_handler import ItemEntityHandler


import moderngl as mgl


class Scene:
    def __init__(self, engine, project) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine, project, and ctx
        self.engine = engine
        self.project = project
        self.ctx = self.engine.ctx

        # Gets handlers from parent project
        self.vao_handler = self.project.vao_handler

        # Creates a chunk handler
        self.chunk_handler = ChunkHandler(self)

        # Creates a free camera and player
        self.player = Player(self)
        self.camera = FirstPersonCamera(self.engine, self, self.player)

        # Item entities
        self.item_entity_handler = ItemEntityHandler(self)

    def use(self):
        """
        Selects this scene for rendering and updating
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.shader_handler.write_all_uniforms()
        self.project.ui_handler.use(self, self.vao_handler.vaos['frame'], self.engine.win_size)
        self.project.texture_handler.write_textures(self.vao_handler.shader_handler.programs['voxel'])
        self.project.texture_handler.write_textures(self.vao_handler.shader_handler.programs['item_entity'])
        self.project.texture_handler.write_textures(self.vao_handler.shader_handler.programs['default'])

    def update(self):
        """
        Updates uniforms, and camera
        """
        
        keys = self.engine.keys
        prev_keys = self.engine.prev_keys

        self.vao_handler.shader_handler.update_uniforms()
        self.camera.update()
        self.player.update()
        self.chunk_handler.update()
        self.item_entity_handler.update()
        self.project.ui_handler.update()

    def render(self):
        """
        Redners all instances
        """

        self.project.texture_handler.framebuffer.clear(color=(0.3, 0.75, 0.9))
        self.project.texture_handler.framebuffer.use()
        self.chunk_handler.render()
        self.player.outline_handler.render()
        self.item_entity_handler.render()

        self.ctx.screen.use()
        self.vao_handler.shader_handler.programs['frame']['frameTexture'] = 0
        self.project.texture_handler.frame_texture.use(location=0)
        self.vao_handler.vaos['frame'].render()


    def release(self):
        """
        Releases scene's VAOs
        """

        self.vao_handler.release()