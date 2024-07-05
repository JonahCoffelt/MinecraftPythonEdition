import pygame as pg
from scripts.camera import Camera
from scripts.chunk_handler import ChunkHandler


class Scene:
    def __init__(self, engine, project) -> None:
        """
        Contains all data for scene
        """

        # Stores the engine, project, and ctx
        self.engine = engine
        self.project = project
        self.ctx = self.engine.ctx
        self.timer = 0

        # Makes a free cam
        self.camera = Camera(self.engine)

        # Gets handlers from parent project
        self.vao_handler = self.project.vao_handler

        # Creates a chunk handler
        self.chunk_handler = ChunkHandler(self)

    def use(self):
        """
        Updates project handlers to use this scene
        """

        self.vao_handler.shader_handler.set_camera(self.camera)
        self.camera.use()
        self.vao_handler.shader_handler.write_all_uniforms()

    def update(self):
        """
        Updates uniforms, and camera
        """
        
        self.vao_handler.shader_handler.update_uniforms()
        self.project.texture_handler.write_textures(self.vao_handler.shader_handler.programs['voxel'])
        self.camera.update()

    def render(self):
        """
        Redners all instances
        """
        self.chunk_handler.render()


    def release(self):
        """
        Releases scene's VAOs
        """

        self.vao_handler.release()