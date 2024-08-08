import glm
import moderngl as mgl
from scripts.vbo_handler import PlaneVBO


class Sky:
    def __init__(self, scene) -> None:
        # Save references
        self.scene = scene
        self.ctx = scene.ctx
        self.vao_handler = scene.vao_handler
        self.programs = self.vao_handler.shader_handler.programs

        # Generate the sky and void planes  
        self.get_planes()
    
    def get_planes(self):
        sky_vbo = PlaneVBO(self.ctx)
        self.sky_vao = self.ctx.vertex_array(self.programs['sky'], [(sky_vbo.vbo, sky_vbo.format, *sky_vbo.attribs)], skip_errors=True)

    def render(self):

        self.ctx.disable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        #self.ctx.disable(flags=mgl.CULL_FACE)

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
        fog_color = (0.75, 0.8, 1.0)
        sky_color = glm.vec3(0.47, 0.66, 1.0)
        void_color = glm.vec3(0.75, 0.8, 1.0)

        self.ctx.clear(color=fog_color)
        #self.ctx.clear(color=(1.0, 1.0, 1.0))

        fog_color = glm.vec3(fog_color)

        # Render sky
        self.programs['sky']['m_model'].write(m_model_sky)
        self.programs['sky']['fogColor'].write(fog_color)
        self.programs['sky']['planeColor'].write(sky_color)
        self.sky_vao.render()

        # Render void
        self.programs['sky']['m_model'].write(m_model_void)
        self.programs['sky']['fogColor'].write(fog_color)
        self.programs['sky']['planeColor'].write(void_color)
        self.sky_vao.render()

        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
