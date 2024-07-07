import numpy as np

class VBOHandler:
    """
    Stores all vertex buffer objects
    """
    def __init__(self, ctx):
        self.ctx = ctx
        self.vbos = {}
        self.vbos['frame'] = FrameVBO(self.ctx)
        self.vbos['cube'] = CubeVBO(self.ctx)

    def load_vbo(self, path: str='vbo'):
        raise RuntimeError('VBOHandler.add_vbo: No support for vbo loading')

    def release(self):
        """
        Releases all VBOs in handler
        """

        [vbo.vbo.release() for vbo in self.vbos.values()]


class BaseVBO:
    """
    Stores vertex data, format, and attributes for VBO
    """

    def __init__(self, ctx):
        self.ctx = ctx
        self.vbo = self.get_vbo()
        self.triangles: list
        self.unique_points: list
        self.format: str = None
        self.attrib: list = None

    def get_vertex_data(self) -> np.ndarray: ...

    @staticmethod
    def get_data(verticies, indicies) -> np.ndarray:
        """
        Formats verticies based on indicies
        """
        data = [verticies[ind] for triangle in indicies for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vbo(self):
        """
        Creates a buffer with the vertex data
        """
        
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)

        verticies = vertex_data[:,:3]

        self.triangles = verticies.reshape((verticies.shape[0]//3, 3, 3)).tolist()
        self.unique_points = []
        [self.unique_points.append(x) for x in verticies.tolist() if x not in self.unique_points]

        return vbo

class FrameVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 2f'
        self.attribs = ['in_position', 'in_texcoord']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],  # Bottom Left
                     [ 1, -1, 0],  # Bottom Right
                     [ 1, 1, 0],   # Top Right
                     [-1, 1, 0],  # Top Left
                     ])
        indicies = [(3, 0, 1),
                    (2, 3, 1)]

        vertex_data = self.get_data(verticies, indicies)

        tex_coord_verticies =   [
                                (0, 0), # Bottom Left
                                (1, 0), # Bottom Right
                                (1, 1), # Top Right
                                (0, 1)  # Top Left
                                ]
        tex_coord_indicies = [(3, 0, 1),
                              (2, 3, 1)]
        tex_coord_data = self.get_data(tex_coord_verticies, tex_coord_indicies)


        vertex_data = np.hstack([vertex_data, tex_coord_data])
        return vertex_data

class CubeVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 3f 2f'
        self.attribs = ['in_position', 'in_normal', 'in_texcoord']

    def get_vertex_data(self):
        verticies = [(-1, -1, 1), ( 1, -1,  1), (1,  1,  1), (-1, 1,  1),
                     (-1,  1,-1), (-1, -1, -1), (1, -1, -1), ( 1, 1, -1)]
        
        indicies = [(0, 2, 3), (0, 1, 2),
                    (1, 7, 2), (1, 6, 7),
                    (6, 5, 4), (4, 7, 6),
                    (3, 4, 5), (3, 5, 0),
                    (3, 7, 4), (3, 2, 7),
                    (0, 6, 1), (0, 5, 6)]

        vertex_data = self.get_data(verticies, indicies)

        tex_coord_verticies = [(0, 0), (1, 0), (1, 1), (0, 1)]
        tex_coord_indicies = [(0, 2, 3), (0, 1, 2),
                              (0, 2, 3), (0, 1, 2),
                              (0, 1, 2), (2, 3, 0),
                              (2, 3, 0), (2, 0, 1),
                              (0, 2, 3), (0, 1, 2),
                              (3, 1, 2), (3, 0, 1)]
        tex_coord_data = self.get_data(tex_coord_verticies, tex_coord_indicies)

        normals = [(0, 0,  1) * 6,
                   ( 1, 0, 0) * 6,
                   (0, 0, -1) * 6,
                   (-1, 0, 0) * 6,
                   (0,  1, 0) * 6,
                   (0, -1, 0) * 6]
        normals = np.array(normals, dtype='f4').reshape(36, 3)

        vertex_data = np.hstack([vertex_data, normals])
        vertex_data = np.hstack([vertex_data, tex_coord_data])
        return vertex_data
    

class FrameVBO(BaseVBO):
    def __init__(self, ctx):
        super().__init__(ctx)
        self.format = '3f 2f'
        self.attribs = ['in_position', 'in_texcoord']

    def get_vertex_data(self):
        verticies = np.array([[-1, -1, 0],  # Bottom Left
                     [ 1, -1, 0],  # Bottom Right
                     [ 1, 1, 0],   # Top Right
                     [-1, 1, 0],  # Top Left
                     ])
        indicies = [(3, 0, 1),
                    (2, 3, 1)]

        vertex_data = self.get_data(verticies, indicies)

        tex_coord_verticies =   [
                                (0, 0), # Bottom Left
                                (1, 0), # Bottom Right
                                (1, 1), # Top Right
                                (0, 1)  # Top Left
                                ]
        tex_coord_indicies = [(3, 0, 1),
                              (2, 3, 1)]
        tex_coord_data = self.get_data(tex_coord_verticies, tex_coord_indicies)


        vertex_data = np.hstack([vertex_data, tex_coord_data])
        return vertex_data