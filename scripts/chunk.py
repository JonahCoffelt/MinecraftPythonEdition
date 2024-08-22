import numpy as np
import glm
from scripts.chunk_mesh import ChunkMeshVBO


class Chunk:
    def __init__(self, scene, chunk_handler, x: int, y: int, z: int, dimension: int=16) -> None:
        # Saves the parent scene and chunk handler
        self.scene = scene
        self.chunk_handler = chunk_handler
        # Create and array for voxel data
        self.voxel_array = np.zeros(shape=(dimension, dimension, dimension), dtype='i8')  # Use the (x, y, z)/[x][y][z] standard for voxel array
        self.light = np.zeros(shape=(dimension, dimension, dimension), dtype='i8')
        self.placed_light = np.zeros(shape=(dimension, dimension, dimension), dtype='i8')
        self.dimension = dimension
        self.position = glm.vec3(x, y, z)
        # Create a mesh object for the chunk
        self.mesh = ChunkMeshVBO(self.scene.ctx, self)
        # Initialize a VAO variable for rendering
        self.vao = None

    def build_vao(self):
        """
        Creates a vao from the chunk voxel data
        """
        
        if self.vao: self.vao.release()

        self.mesh.build_mesh()

        shader_handler = self.scene.vao_handler.shader_handler
        self.vao = self.scene.ctx.vertex_array(shader_handler.programs['voxel'], [(self.mesh.vbo, self.mesh.format, *self.mesh.attribs)], skip_errors=True)

    def render(self):
        if not self.vao: return

        m_model = glm.mat4()
        m_model = glm.translate(m_model, self.position * self.dimension)
        self.scene.vao_handler.shader_handler.programs['voxel']['m_model'].write(m_model)
        
        self.vao.render()

    def set_voxel(self, x: int, y: int, z: int, id: int=0) -> None:
        """
        Sets a voxel given in local coordinates to the given voxel id
        """

        self.voxel_array[x][y][z] = id
