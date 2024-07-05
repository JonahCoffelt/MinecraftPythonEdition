import numpy as np
from numba import njit


@njit
def add_data(vertex_data, index, *verticies):
    for vertex in verticies:
        for value in vertex:
            vertex_data[index] = value
            index += 1
    return index


@njit
def is_empty(chunk_voxels, x, y, z):
    dim = chunk_voxels.shape[0]
    
    # Check if the voxel is outside of the chunk
    if not (0 <= x < dim and 0 <= y < dim and 0 <= z < dim): return True

    return not bool(chunk_voxels[x][y][z])

@njit
def get_mesh_buffer(chunk_voxels):
    dim = chunk_voxels.shape[0]
    vertex_data = np.zeros((dim ** 3 + 1) * 5 * 36, dtype='uint8')
    index = 5 * 36
    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                if not chunk_voxels[x][y][z]: continue

                id = chunk_voxels[x][y][z]

                # Front
                if is_empty(chunk_voxels, x, y, z + 1):
                    face = 5
                    index = add_data(vertex_data, index, 
                                        (x    , y    , z + 1, id, face), (x + 1, y + 1, z + 1, id, face), (x    , y + 1, z + 1, id, face), 
                                        (x    , y    , z + 1, id, face), (x + 1, y    , z + 1, id, face), (x + 1, y + 1, z + 1, id, face))

                # Back
                if is_empty(chunk_voxels, x, y, z - 1):
                    face = 4
                    index = add_data(vertex_data, index, 
                                        (x    , y    , z    , id, face), (x    , y + 1, z    , id, face), (x + 1, y + 1, z    , id, face), 
                                        (x    , y    , z    , id, face), (x + 1, y + 1, z    , id, face), (x + 1, y    , z    , id, face))

                # Top
                if is_empty(chunk_voxels, x, y + 1, z):
                    face = 0
                    index = add_data(vertex_data, index, 
                                        (x    , y + 1, z    , id, face), (x    , y + 1, z + 1, id, face), (x + 1, y + 1, z + 1, id, face), 
                                        (x    , y + 1, z    , id, face), (x + 1, y + 1, z + 1, id, face), (x + 1, y + 1, z    , id, face))

                # Bottom
                if is_empty(chunk_voxels, x, y - 1, z):
                    face = 1
                    index = add_data(vertex_data, index, 
                                        (x    , y    , z    , id, face), (x + 1, y    , z + 1, id, face), (x    , y    , z + 1, id, face), 
                                        (x    , y    , z    , id, face), (x + 1, y    , z    , id, face), (x + 1, y    , z + 1, id, face))

                # Right
                if is_empty(chunk_voxels, x + 1, y, z):
                    face = 2
                    index = add_data(vertex_data, index,
                                        (x + 1, y    , z    , id, face), (x + 1, y + 1, z    , id, face), (x + 1, y + 1, z + 1, id, face),
                                        (x + 1, y    , z    , id, face), (x + 1, y + 1, z + 1, id, face), (x + 1, y    , z + 1, id, face))

                # Left
                if is_empty(chunk_voxels, x - 1, y, z):
                    face = 3
                    index = add_data(vertex_data, index,
                                        (x    , y    , z    , id, face), (x    , y + 1, z + 1, id, face), (x    , y + 1, z    , id, face),
                                        (x    , y    , z    , id, face), (x    , y    , z + 1, id, face), (x    , y + 1, z + 1, id, face))

    return vertex_data[:index]


class ChunkMeshVBO:
    """
    Stores vertex data, format, and attributes for VBO
    """

    def __init__(self, ctx, chunk):
        self.ctx = ctx
        self.chunk = chunk
        self.vbo = None
        self.build_mesh()
        self.format = '3u1 1u1 1u1'
        self.attribs = ['in_position', 'in_id', 'in_face']

    def build_mesh(self):
        """
        Creates a mesh buffer of the given chunks voxel data
        """

        if self.vbo: self.vbo.release()

        self.vbo = self.ctx.buffer(get_mesh_buffer(self.chunk.voxel_array))