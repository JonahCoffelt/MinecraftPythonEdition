from scripts.vbo_handler import VBOHandler
from scripts.shader_handler import ShaderHandler


class VAOHandler:
    """
    Stores VBO and shader handlers. Creates VAOs
    """
    def __init__(self, project):
        self.project = project
        self.ctx = self.project.ctx
    
        self.shader_handler = ShaderHandler(self.project)
        self.vbo_handler = VBOHandler(self.ctx)

        self.vaos = {}
        self.vao_to_vbo_key = {}

        self.add_vao('frame', 'frame', 'quad')
        self.add_vao('cube', 'voxel', 'cube')
        self.add_vao('outline', 'outline', 'outline')
        self.add_vao('mining', 'default', 'cube')

    def add_vao(self, name: str='cube', program_key: str='voxel', vbo_key: str='cube'):
        """
        Adds a new VAO with a program and VBO. Creates an empty instance buffer
        """

        # Gets program and vbo
        program = self.shader_handler.programs[program_key]
        vbo = self.vbo_handler.vbos[vbo_key]
        vao = self.ctx.vertex_array(program, [(vbo.vbo, vbo.format, *vbo.attribs)], skip_errors=True)
        self.vaos[name], self.vao_to_vbo_key[name] = vao, vbo_key
    
    def release(self):
        """
        Releases all VAOs and shader programs in handler
        """
        
        self.vbo_handler.release()
        self.shader_handler.release()