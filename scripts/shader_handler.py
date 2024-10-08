import moderngl as mgl
import glm
import numpy as np

# Predefined uniforms that do not change each frame
single_frame_uniforms = []


class ShaderHandler:
    def __init__(self, project) -> None:
        self.project = project
        self.ctx = self.project.ctx
        self.programs = {}
        self.uniform_attribs = {}

        self.programs['frame'] = self.load_program('frame')
        self.programs['voxel'] = self.load_program('voxel')
        self.programs['outline'] = self.load_program('outline')
        self.programs['default'] = self.load_program('default')
        self.programs['item_entity'] = self.load_program('item_entity')
        self.programs['sky'] = self.load_program('sky')

    def load_program(self, name: str='default') -> mgl.Program:
        """
        Creates a shader program from a file name.
        Parses through shaders to identify uniforms and save for writting
        """

        # Read the shaders
        with open(f'shaders/{name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{name}.frag') as file:
            fragment_shader = file.read()
            
        # Create blank list for uniforms
        self.uniform_attribs[name] = []
        # Create a list of all lines in both shaders
        lines = f'{vertex_shader}\n{fragment_shader}'.split('\n')
        # Parse through shader to find uniform variables
        for line in lines:
            tokens = line.strip().split(' ')
            if tokens[0] == 'uniform' and len(tokens) > 2:
                self.uniform_attribs[name].append(tokens[2][:-1])

        # Create a program with shaders
        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def set_camera(self, camera):
        """
        Sets the camera. Allows for camera switching between any camera in the project        
        """

        self.camera = camera

    def get_all_uniforms(self) -> None:
        """
        Gets uniforms from various parts of the scene.
        These values are stored and used in write_all_uniforms and update_uniforms.
        This is called by write_all_uniforms and update_uniforms, so there is no need to call this manually.
        """
        
        self.uniform_values = {
            'm_proj' : self.camera.m_proj,
            'm_view' : self.camera.m_view,
            'm_model' : glm.mat4(),
            'cameraPosition' : self.camera.position,
            'winSize' : glm.vec2(*self.project.engine.win_size),
        }

    def write_all_uniforms(self) -> None:
        """
        Writes all of the uniforms in every shader program.
        This should only be used on the first frame or to reset uniforms
        """

        self.get_all_uniforms()
        for uniform in self.uniform_values:
            for program in self.programs:
                if not uniform in self.uniform_attribs[program]: continue  # Does not write uniforms not in the shader
                self.programs[program][uniform].write(self.uniform_values[uniform])

    def update_uniforms(self) -> None:
        """
        Updates uniforms that are likely to change each frame
        Ideal to call once every frame
        """

        self.get_all_uniforms()
        for uniform in self.uniform_values:
            if uniform in single_frame_uniforms: continue  # Does not write uniforms that dont update each frame
            for program in self.programs:
                if not uniform in self.uniform_attribs[program]: continue  # Does not write uniforms not in the shader
                self.programs[program][uniform].write(self.uniform_values[uniform])

    def get_block_textures(self):
        # Load textures
        with open('gamedata/texture_paths.txt', 'r') as file:
            file_list = list(file)
            for line in file_list:
                self.project.texture_handler.load_texture(line.strip() + '.png')
        # Generate Array
        self.project.texture_handler.generate_texture_arrays()
        # Load Block Texture IDs
        with open('gamedata/block_textures.txt', 'r') as file:
            file_list = list(file)
            texture_ids = []
            for line in file_list[1:]:
                line = line.strip().split(',')[1:]
                for id in line:
                    texture_ids.append(int(id.strip()))
        
        texture_ids = np.array(texture_ids, dtype='i4')

        self.programs['voxel']['textures'].write(texture_ids)

    def release(self) -> None:
        """
        Releases all shader programs in handler
        """
        
        [program.release() for program in self.programs.values()]