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
def is_empty(neighbors, x, y, z):
    dim = neighbors[1][1][1].shape[0]
    
    chunk_x, chunk_y, chunk_z = x // dim, y // dim, z // dim
    local_x, local_y, local_z = x % dim, y % dim, z % dim

    return not bool(neighbors[chunk_x + 1][chunk_y + 1][chunk_z + 1][local_x][local_y][local_z])

@njit
def get_light(neighbors_light, x, y, z):
    dim = neighbors_light[1][1][1].shape[0]
    
    chunk_x, chunk_y, chunk_z = x // dim, y // dim, z // dim
    local_x, local_y, local_z = x % dim, y % dim, z % dim

    return neighbors_light[chunk_x + 1][chunk_y + 1][chunk_z + 1][local_x][local_y][local_z]

@njit
def get_placed_light(neighbors_placed_light, x, y, z):
    dim = neighbors_placed_light[1][1][1].shape[0]
    
    chunk_x, chunk_y, chunk_z = x // dim, y // dim, z // dim
    local_x, local_y, local_z = x % dim, y % dim, z % dim

    return neighbors_placed_light[chunk_x + 1][chunk_y + 1][chunk_z + 1][local_x][local_y][local_z]

@njit
def get_face_ao(neighbors, plane, x, y, z):
    if plane == 'y':
        v0 = is_empty(neighbors, *(x    , y    , z - 1))
        v1 = is_empty(neighbors, *(x - 1, y    , z - 1))
        v2 = is_empty(neighbors, *(x - 1, y    , z    ))
        v3 = is_empty(neighbors, *(x - 1, y    , z + 1))
        v4 = is_empty(neighbors, *(x    , y    , z + 1))
        v5 = is_empty(neighbors, *(x + 1, y    , z + 1))
        v6 = is_empty(neighbors, *(x + 1, y    , z    ))
        v7 = is_empty(neighbors, *(x + 1, y    , z - 1))

    elif plane == 'x':
        v0 = is_empty(neighbors, *(x    , y    , z - 1))
        v1 = is_empty(neighbors, *(x    , y - 1, z - 1))
        v2 = is_empty(neighbors, *(x    , y - 1, z    ))
        v3 = is_empty(neighbors, *(x    , y - 1, z + 1))
        v4 = is_empty(neighbors, *(x    , y    , z + 1))
        v5 = is_empty(neighbors, *(x    , y + 1, z + 1))
        v6 = is_empty(neighbors, *(x    , y + 1, z    ))
        v7 = is_empty(neighbors, *(x    , y + 1, z - 1))

    else:
        v0 = is_empty(neighbors, *(x - 1, y    , z    ))
        v1 = is_empty(neighbors, *(x - 1, y - 1, z    ))
        v2 = is_empty(neighbors, *(x    , y - 1, z    ))
        v3 = is_empty(neighbors, *(x + 1, y - 1, z    ))
        v4 = is_empty(neighbors, *(x + 1, y    , z    ))
        v5 = is_empty(neighbors, *(x + 1, y + 1, z    ))
        v6 = is_empty(neighbors, *(x    , y + 1, z    ))
        v7 = is_empty(neighbors, *(x - 1, y + 1, z    ))

    return (v0 + v1 + v2), (v6 + v7 + v0), (v4 + v5 + v6), (v2 + v3 + v4)


@njit
def get_mesh_buffer(chunk_voxels, neighbors, neighbors_light, neighbors_placed_light):
    dim = chunk_voxels.shape[0]
    vertex_data = np.zeros((dim ** 3 + 1) * 8 * 36, dtype='uint8')
    index = 8 * 36
    for x in range(dim):
        for y in range(dim):
            for z in range(dim):
                if not chunk_voxels[x][y][z]: continue

                id = chunk_voxels[x][y][z]

                # Front
                if is_empty(neighbors, x, y, z + 1):
                    ao = get_face_ao(neighbors, 'z', x, y, z + 1)

                    light_level = get_light(neighbors_light, x, y, z + 1)
                    placed_light_level = get_placed_light(neighbors_placed_light, x, y, z + 1)

                    face = 5
                    index = add_data(vertex_data, index, 
                                        (x    , y    , z + 1, id, face, ao[0], light_level, placed_light_level), (x + 1, y + 1, z + 1, id, face, ao[2], light_level, placed_light_level), (x    , y + 1, z + 1, id, face, ao[1], light_level, placed_light_level), 
                                        (x    , y    , z + 1, id, face, ao[0], light_level, placed_light_level), (x + 1, y    , z + 1, id, face, ao[3], light_level, placed_light_level), (x + 1, y + 1, z + 1, id, face, ao[2], light_level, placed_light_level))

                # Back
                if is_empty(neighbors, x, y, z - 1):
                    ao = get_face_ao(neighbors, 'z', x, y, z - 1)

                    light_level = get_light(neighbors_light, x, y, z - 1)
                    placed_light_level = get_placed_light(neighbors_placed_light, x, y, z - 1)

                    face = 4
                    index = add_data(vertex_data, index, 
                                        (x    , y    , z    , id, face, ao[0], light_level, placed_light_level), (x    , y + 1, z    , id, face, ao[1], light_level, placed_light_level), (x + 1, y + 1, z    , id, face, ao[2], light_level, placed_light_level), 
                                        (x    , y    , z    , id, face, ao[0], light_level, placed_light_level), (x + 1, y + 1, z    , id, face, ao[2], light_level, placed_light_level), (x + 1, y    , z    , id, face, ao[3], light_level, placed_light_level))

                # Top
                if is_empty(neighbors, x, y + 1, z):
                    ao = get_face_ao(neighbors, 'y', x, y + 1, z)

                    light_level = get_light(neighbors_light, x, y + 1, z)
                    placed_light_level = get_placed_light(neighbors_placed_light, x, y + 1, z)

                    face = 0
                    index = add_data(vertex_data, index, 
                                        (x    , y + 1, z    , id, face, ao[0], light_level, placed_light_level), (x    , y + 1, z + 1, id, face, ao[3], light_level, placed_light_level), (x + 1, y + 1, z + 1, id, face, ao[2], light_level, placed_light_level), 
                                        (x    , y + 1, z    , id, face, ao[0], light_level, placed_light_level), (x + 1, y + 1, z + 1, id, face, ao[2], light_level, placed_light_level), (x + 1, y + 1, z    , id, face, ao[1], light_level, placed_light_level))

                # Bottom
                if is_empty(neighbors, x, y - 1, z):
                    ao = get_face_ao(neighbors, 'y', x, y - 1, z)

                    light_level = get_light(neighbors_light, x, y - 1, z)
                    placed_light_level = get_placed_light(neighbors_placed_light, x, y - 1, z)

                    face = 1
                    index = add_data(vertex_data, index, 
                                        (x    , y    , z    , id, face, ao[0], light_level, placed_light_level), (x + 1, y    , z + 1, id, face, ao[2], light_level, placed_light_level), (x    , y    , z + 1, id, face, ao[3], light_level, placed_light_level), 
                                        (x    , y    , z    , id, face, ao[0], light_level, placed_light_level), (x + 1, y    , z    , id, face, ao[1], light_level, placed_light_level), (x + 1, y    , z + 1, id, face, ao[2], light_level, placed_light_level))

                # Right
                if is_empty(neighbors, x + 1, y, z):
                    ao = get_face_ao(neighbors, 'x', x + 1, y, z)

                    light_level = get_light(neighbors_light, x + 1, y, z)
                    placed_light_level = get_placed_light(neighbors_placed_light, x + 1, y, z)

                    face = 2
                    index = add_data(vertex_data, index,
                                        (x + 1, y    , z    , id, face, ao[0], light_level, placed_light_level), (x + 1, y + 1, z    , id, face, ao[1], light_level, placed_light_level), (x + 1, y + 1, z + 1, id, face, ao[2], light_level, placed_light_level),
                                        (x + 1, y    , z    , id, face, ao[0], light_level, placed_light_level), (x + 1, y + 1, z + 1, id, face, ao[2], light_level, placed_light_level), (x + 1, y    , z + 1, id, face, ao[3], light_level, placed_light_level))

                # Left
                if is_empty(neighbors, x - 1, y, z):
                    ao = get_face_ao(neighbors, 'x', x - 1, y, z)

                    light_level = get_light(neighbors_light, x - 1, y, z)
                    placed_light_level = get_placed_light(neighbors_placed_light, x - 1, y, z)

                    face = 3
                    index = add_data(vertex_data, index,
                                        (x    , y    , z    , id, face, ao[0], light_level, placed_light_level), (x    , y + 1, z + 1, id, face, ao[2], light_level, placed_light_level), (x    , y + 1, z    , id, face, ao[1], light_level, placed_light_level),
                                        (x    , y    , z    , id, face, ao[0], light_level, placed_light_level), (x    , y    , z + 1, id, face, ao[3], light_level, placed_light_level), (x    , y + 1, z + 1, id, face, ao[2], light_level, placed_light_level))

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
        self.format = '3u1 1u1 1u1 1u1 1u1 1u1'
        self.attribs = ['in_position', 'in_id', 'in_face', 'in_ao', 'in_light_level', 'in_placed_light_level']

    def build_mesh(self):
        """
        Creates a mesh buffer of the given chunks voxel data
        """

        if self.vbo: self.vbo.release()

        neighbors = self.chunk.chunk_handler.get_neighbor_chunk_arrays(*self.chunk.position.xyz)
        neighbors_light = self.chunk.chunk_handler.get_neighbor_chunk_light(*self.chunk.position.xyz)
        neighbors_placed_light = self.chunk.chunk_handler.get_neighbor_placed_light(*self.chunk.position.xyz)

        self.vbo = self.ctx.buffer(get_mesh_buffer(self.chunk.voxel_array, neighbors, neighbors_light, neighbors_placed_light))