import glm
import numpy as np
import moderngl as mgl
from scripts.vbo_handler import PlaneVBO


class Sky:
    def __init__(self, scene) -> None:
        # Save references
        self.scene = scene
        self.ctx = scene.ctx
        self.vao_handler = scene.vao_handler
        self.programs = self.vao_handler.shader_handler.programs

        # Game time
        self.time = 0
        self.internal_sky_light = 15

        # Time sky parameters
        self.sky_times = {
            0 :  (glm.vec3(0.47, 0.66, 1.0),    glm.vec3(0.75, 0.8, 1.0),   glm.vec3(0.75, 0.8, 1.0),   15), # Day Start
            11 : (glm.vec3(0.47, 0.66, 1.0),    glm.vec3(0.75, 0.8, 1.0),   glm.vec3(0.75, 0.8, 1.0),   15), # Day End
            12 : (glm.vec3(0.42, 0.48, 0.68),   glm.vec3(0.84, 0.51, 0.28), glm.vec3(0.84, 0.51, 0.28), 7), # Dusk
            13 : (glm.vec3(0, 0, 0),            glm.vec3(0.04, 0.05, 0.08), glm.vec3(0.04, 0.05, 0.08), 0), # Night Start
            22 : (glm.vec3(0, 0, 0),            glm.vec3(0.04, 0.05, 0.08), glm.vec3(0.04, 0.05, 0.08), 0), # Night End
            23 : (glm.vec3(0.12, 0.18, 0.3),    glm.vec3(0.8, 0.4, 0.25),   glm.vec3(0.8, 0.4, 0.25),   7), # Sunrise
            24 : (glm.vec3(0.47, 0.66, 1.0),    glm.vec3(0.75, 0.8, 1.0),   glm.vec3(0.75, 0.8, 1.0),   15), # Day Start
        }
        self.times = np.array(list(self.sky_times.keys()))

        # Generate the sky and void planes  
        self.get_planes()
    
    def get_planes(self):
        sky_vbo = PlaneVBO(self.ctx)
        self.sky_vao = self.ctx.vertex_array(self.programs['sky'], [(sky_vbo.vbo, sky_vbo.format, *sky_vbo.attribs)], skip_errors=True)

    def update(self, dt):
        self.time += dt * 3
        self.time = self.time % 24

        time_index = np.searchsorted(self.times, self.time)

        time_key_1, time_key_2 = self.times[time_index - 1], self.times[time_index%len(self.sky_times)]
        sky_color_1, sky_color_2 = self.sky_times[time_key_1], self.sky_times[time_key_2]

        self.sky_color  = (sky_color_2[0] - sky_color_1[0]) / (time_key_2 - time_key_1) * (self.time - time_key_1) + sky_color_1[0]
        self.fog_color  = (sky_color_2[1] - sky_color_1[1]) / (time_key_2 - time_key_1) * (self.time - time_key_1) + sky_color_1[1]
        self.void_color = (sky_color_2[2] - sky_color_1[2]) / (time_key_2 - time_key_1) * (self.time - time_key_1) + sky_color_1[2]
        self.internal_sky_light = (sky_color_2[3] - sky_color_1[3]) / (time_key_2 - time_key_1) * (self.time - time_key_1) + sky_color_1[3]

        self.programs['voxel']['internal_sky_light'].write(glm.float32(self.internal_sky_light))

    def render(self):

        self.ctx.disable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

        # Get Model Matrix
        m_model_sky = glm.mat4()
        m_model_void = glm.mat4()

        # Translate
        position = self.scene.camera.position
        position.y += 10.0
        m_model_sky = glm.translate(m_model_sky, position)
        position.y -= 20.0
        m_model_void = glm.translate(m_model_void, position)

        # Scale
        m_model_sky = glm.scale(m_model_sky, glm.vec3(200.0, 0.0, 200.0))
        m_model_void = glm.scale(m_model_void, glm.vec3(200.0, 0.0, 200.0))

        # Sunset
        # fog_color = (0.8, 0.4, 0.25)
        # sky_color = glm.vec3(0.12, 0.18, 0.3)
        # void_color = glm.vec3(0.12, 0.18, 0.3)

        # Day
        # fog_color = (0.75, 0.8, 1.0)
        # sky_color = glm.vec3(0.47, 0.66, 1.0)
        # void_color = glm.vec3(0.75, 0.8, 1.0)

        self.ctx.clear(color=self.fog_color)
        self.programs['sky']['fogColor'].write(self.fog_color)

        # Render sky
        self.programs['sky']['m_model'].write(m_model_sky)
        self.programs['sky']['planeColor'].write(self.sky_color)
        self.sky_vao.render()

        # Render void
        self.programs['sky']['m_model'].write(m_model_void)
        self.programs['sky']['planeColor'].write(self.void_color)
        self.sky_vao.render()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
